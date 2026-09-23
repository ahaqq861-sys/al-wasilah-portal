from django.db import models
from django.contrib.auth.models import User

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default="AL WASILAH SCHOOL COMPLEX")
    motto = models.CharField(max_length=255, default="Knowledge and Excellence")
    postal_address = models.CharField(max_length=255, blank=True, null=True, default="P.O. Box 123")
    phone_numbers = models.CharField(max_length=100, blank=True, null=True, default="0240000000")
    email = models.EmailField(blank=True, null=True, default="info@alwasilah.com")
    primary_color = models.CharField(max_length=10, default="#1e7e34")
    secondary_color = models.CharField(max_length=10, default="#ffffff")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    current_academic_year = models.CharField(max_length=20, default="2026/2027")
    current_term = models.CharField(max_length=50, default="FIRST TRIMESTER")

    def __str__(self):
        return self.school_name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    index_number = models.CharField(max_length=50, unique=True)
    assigned_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.index_number})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    assigned_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_class}"

class GradeReport(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grade_reports')
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    class_score = models.FloatField(default=0.0)
    exam_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    grade = models.CharField(max_length=5, blank=True)

    def save(self, *args, **kwargs):
        self.total_score = self.class_score + self.exam_score
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