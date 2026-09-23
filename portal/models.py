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

class SchoolBranding(models.Model):
    school_name = models.CharField(max_length=255, default='AL WASILAH SCHOOL COMPLEX')
    motto = models.CharField(max_length=255, default='KNOWLEDGE, INTEGRITY AND EXCELLENCE')
    postal_address = models.CharField(max_length=255, default='P.O.Box 161 TL')
    phone_numbers = models.CharField(max_length=255, default='0244963410 / 0246849302 / 0243881080')
    email = models.EmailField(default='alwasilaschool2026@gmail.com')
    primary_color = models.CharField(max_length=20, default='#6b1d2f')
    secondary_color = models.CharField(max_length=20, default='#d4af37')
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    current_academic_year = models.CharField(max_length=20, default='2025/2026')
    current_term = models.CharField(max_length=20, default='Term 1')

    def __str__(self):
        return self.school_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, default='')
    class_assigned = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

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
    age = models.IntegerField(default=5)
    gender = models.CharField(max_length=10, choices=(('MALE', 'Male'), ('FEMALE', 'Female')), default='MALE')
    nationality = models.CharField(max_length=50, default='GHANAIAN')
    fee_category = models.CharField(max_length=30, default='REGULAR')
    program_name = models.CharField(max_length=100, default='BASIC EDUCATION')
    passport_photo = models.ImageField(upload_to='students/passports/', null=True, blank=True)
    parent_name = models.CharField(max_length=100, blank=True, default='')
    parent_contact = models.CharField(max_length=50, blank=True, default='')
    parent_email = models.EmailField(blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} [{self.index_number}]"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_data')
    staff_id = models.CharField(max_length=30, unique=True)
    class_assigned = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES)
    gender = models.CharField(max_length=10, choices=(('MALE', 'Male'), ('FEMALE', 'Female')), default='MALE')
    age = models.IntegerField(default=25)
    passport_photo = models.ImageField(upload_to='teachers/passports/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_class_assigned_display()}"

class GradeReport(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='grades')
    subject_code = models.CharField(max_length=20, default='SUB101')
    subject_name = models.CharField(max_length=100)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_mark = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade = models.CharField(max_length=5, default='A')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_mark = float(self.class_score) + float(self.exam_score)
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

class SchoolDocument(models.Model):
    title = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class_level = models.CharField(max_length=20, choices=CLASS_LEVEL_CHOICES, null=True, blank=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title