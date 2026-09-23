from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default="AL-WASILAH SCHOOL COMPLEX")
    motto = models.CharField(max_length=255, default="Knowledge and Excellence")
    postal_address = models.CharField(max_length=255, blank=True, null=True, default="P.O. Box 123, Tamale")
    phone_numbers = models.CharField(max_length=100, blank=True, null=True, default="+233 24 000 0000 / +233 20 000 0000")
    email = models.EmailField(blank=True, null=True, default="info@alwasilah.edu.gh")
    primary_color = models.CharField(max_length=10, default="#800020")  # Wine Color
    secondary_color = models.CharField(max_length=10, default="#ffffff")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True, default="https://via.placeholder.com/120?text=Logo")
    current_academic_year = models.CharField(max_length=20, default="2026/2027")
    current_term = models.CharField(max_length=50, default="FIRST TRIMESTER")

    def __str__(self):
        return self.school_name

class AcademicTerm(models.Model):
    name = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=50)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.academic_year} - {self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=20, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    index_number = models.CharField(max_length=50, unique=True, default="N/A")
    uin = models.CharField(max_length=50, blank=True, null=True)
    assigned_class = models.CharField(max_length=50, default="General")
    class_level = models.CharField(max_length=50, blank=True, null=True, default="Form 1")
    program_name = models.CharField(max_length=100, blank=True, null=True)
    fee_category = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True, default="Ghanaian")
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_contact = models.CharField(max_length=50, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    passport_photo = models.ImageField(upload_to='students/passports/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.index_number})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    staff_id = models.CharField(max_length=50, blank=True, null=True)
    assigned_class = models.CharField(max_length=50, default="General")
    class_assigned = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    passport_photo = models.ImageField(upload_to='teachers/passports/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_class}"

class GradeReport(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grade_reports')
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    term = models.CharField(max_length=50, blank=True, null=True)
    credit_hours = models.IntegerField(default=3)
    class_score = models.FloatField(default=0.0)
    exam_score = models.FloatField(default=0.0)
    total_mark = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    grade = models.CharField(max_length=5, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        self.total_score = self.class_score + self.exam_score
        self.total_mark = self.total_score
        if self.total_score >= 80: self.grade = 'A'
        elif self.total_score >= 70: self.grade = 'B'
        elif self.total_score >= 60: self.grade = 'C'
        elif self.total_score >= 50: self.grade = 'D'
        else: self.grade = 'F'
        super().save(*args, **kwargs)

class FeeLedger(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_ledgers')
    description = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.balance = self.amount_due - self.amount_paid
        super().save(*args, **kwargs)

class LedgerEntry(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ledger_entries')
    description = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class SchoolDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)