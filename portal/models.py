from django.db import models
from django.contrib.auth.models import User

class PortalBranding(models.Model):
    school_name = models.CharField(max_length=255, default="Al-Wasilah Basic School")
    motto = models.CharField(max_length=255, default="Excellence and Integrity")
    logo = models.ImageField(upload_to="branding/", null=True, blank=True)
    primary_color = models.CharField(max_length=20, default="#5c1825")  # Deep Wine
    accent_color = models.CharField(max_length=20, default="#e6b800")   # Gold
    contact_email = models.EmailField(default="info@alwasilah.edu.gh")
    contact_phone = models.CharField(max_length=50, default="+233 24 000 0000")
    address = models.TextField(default="Tamale, Ghana")
    current_academic_year = models.CharField(max_length=20, default="2026/2027")
    current_term = models.CharField(max_length=20, default="FIRST TRIMESTER")

    def __str__(self):
        return self.school_name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    index_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    uin = models.CharField(max_length=50, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    
    # Extended Personal Details
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE')
    age = models.PositiveIntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, default="GHANA")
    disability_status = models.CharField(max_length=255, default="None")
    
    # Academic & Program Details
    programme = models.CharField(max_length=150, default="BASIC EDUCATION")
    assigned_class = models.CharField(max_length=100, default="Basic 1")
    level = models.CharField(max_length=20, default="100")
    fee_category = models.CharField(max_length=50, default="REGULAR")

    # Parent / Guardian Details
    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_phone = models.CharField(max_length=50, null=True, blank=True)
    guardian_relationship = models.CharField(max_length=50, null=True, blank=True)
    guardian_address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class StatementOfResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    academic_year = models.CharField(max_length=20)
    trimester = models.CharField(max_length=50) # e.g. FIRST TRIMESTER
    course_code = models.CharField(max_length=20)
    course_title = models.CharField(max_length=150)
    credit_hours = models.IntegerField(default=3)
    mark = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.student.username} - {self.course_code}"


class FeeLedgerEntry(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_entries')
    date = models.DateField()
    academic_year = models.CharField(max_length=20)
    billing = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    narration = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.student.username} - {self.narration}"