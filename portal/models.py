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
    index_number = models.CharField(max_length=30, unique=True)
    uin = models.CharField(max_length=30, unique=True, blank=True, null=True)
    class_level = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES)
    gender = models.CharField(max_length=10, choices=(('MALE', 'Male'), ('FEMALE', 'Female')), default='MALE')
    nationality = models.CharField(max_length=50, default='GHANAIAN')
    fee_category = models.CharField(max_length=30, default='REGULAR')
    program_name = models.CharField(max_length=100, default='BASIC EDUCATION')
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} [{self.index_number}]"

class GradeReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject_code = models.CharField(max_length=20, default='SUB101')
    subject_name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(default=3)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade = models.CharField(max_length=5, default='A')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_mark = self.class_score + self.exam_score
        if self.total_mark >= 80:
            self.grade = 'A'
        elif self.total_mark >= 70:
            self.grade = 'B'
        elif self.total_mark >= 60:
            self.grade = 'C'
        elif self.total_mark >= 50:
            self.grade = 'D'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject_name}"

class LedgerEntry(models.Model):
    ENTRY_TYPES = (
        ('BILLING', 'Billing'),
        ('PAYMENT', 'Payment'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='ledger_entries')
    academic_year = models.CharField(max_length=20, default='2025/2026')
    date = models.DateField(default=timezone.now)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    narration = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.entry_type} - GH¢{self.amount}"