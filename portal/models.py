from django.db import models
from django.contrib.auth.models import User

class PortalBranding(models.Model):
    school_name = models.CharField(max_length=255, default="AL-WASILAH SCHOOL COMPLEX")
    tagline_subtext = models.CharField(max_length=255, default="Excellence in Academic & Moral Training")
    primary_color = models.CharField(max_length=10, default="#800020") # Wine/Burgundy
    secondary_color = models.CharField(max_length=10, default="#17a2b8")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    contact_email = models.EmailField(default="info@alwasilah.edu.gh")
    contact_phone = models.CharField(max_length=20, default="+233 24 000 0000")
    address = models.TextField(default="Tamale, Northern Region, Ghana")
    footer_text = models.CharField(max_length=255, default="Copyright © 2026 Al-Wasilah School Complex. All rights reserved.")

    def __str__(self):
        return self.school_name

class StudentProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    index_number = models.CharField(max_length=50, blank=True, null=True)
    generated_password = models.CharField(max_length=100, default="ChangeMe123!")
    assigned_class = models.CharField(max_length=50, default="Primary 1")
    programme = models.CharField(max_length=100, default="BASIC EDUCATION CURRICULUM")
    gender = models.CharField(max_length=10, default="MALE")
    passport_picture = models.ImageField(upload_to="passports/", blank=True, null=True)
    can_brand_portal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class FeeLedger(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_entries')
    title = models.CharField(max_length=200)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    academic_year = models.CharField(max_length=20, default="2026/2027")
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"

class AcademicResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='academic_results')
    subject_name = models.CharField(max_length=100)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    grade = models.CharField(max_length=5, blank=True, null=True)
    position_in_subject = models.CharField(max_length=20, blank=True, null=True)
    academic_term = models.CharField(max_length=50, default="Term 1")
    academic_year = models.CharField(max_length=20, default="2026/2027")

    def save(self, *args, **kwargs):
        self.total_score = float(self.class_score) + float(self.exam_score)
        if self.total_score >= 80:
            self.grade = 'A'
        elif self.total_score >= 70:
            self.grade = 'B'
        elif self.total_score >= 60:
            self.grade = 'C'
        elif self.total_score >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.subject_name}"