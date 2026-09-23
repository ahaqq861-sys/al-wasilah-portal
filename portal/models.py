from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

ROLE_CHOICES = (
    ('admin', 'Administrator'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
    ('parent', 'Parent'),
)

CLASS_LEVEL_CHOICES = (
    ('creche', 'Creche'),
    ('nursery_1', 'Nursery 1'),
    ('nursery_2', 'Nursery 2'),
    ('kg_1', 'KG 1'),
    ('kg_2', 'KG 2'),
    ('primary_1', 'Primary 1'),
    ('primary_2', 'Primary 2'),
    ('primary_3', 'Primary 3'),
    ('primary_4', 'Primary 4'),
    ('primary_5', 'Primary 5'),
    ('primary_6', 'Primary 6'),
    ('jhs_1', 'JHS 1'),
    ('jhs_2', 'JHS 2'),
    ('jhs_3', 'JHS 3'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, default='')
    class_assigned = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='Al-Wasilah School Complex')
    motto = models.CharField(max_length=255, default='Knowledge, Virtue & Excellence')
    logo_url = models.URLField(blank=True, default='')
    current_academic_year = models.CharField(max_length=20, default='2025/2026')
    current_term = models.CharField(max_length=20, default='Term 1')

    def __str__(self):
        return self.school_name

class AcademicTerm(models.Model):
    name = models.CharField(max_length=50, default='Term 1')
    academic_year = models.CharField(max_length=20, default='2025/2026')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_data')
    student_id = models.CharField(max_length=30, unique=True)
    class_level = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} [{self.student_id}]"

class GradeReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject = models.CharField(max_length=100)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student} - {self.subject}"

class FeeStatement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fees')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    total_billed = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Fees: {self.student}"