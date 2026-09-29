from django.db import models
from django.contrib.auth.models import User

class PortalBranding(models.Model):
    school_name = models.CharField(max_length=255, default="AL-WASILAH SCHOOL COMPLEX")
    tagline_subtext = models.CharField(max_length=255, default="Excellence and Morality")
    primary_color = models.CharField(max_length=7, default="#800020")
    secondary_color = models.CharField(max_length=7, default="#17a2b8")
    sidebar_color = models.CharField(max_length=7, default="#1e2229")
    contact_phone = models.CharField(max_length=50, default="+233 24 000 0000")
    contact_email = models.EmailField(default="info@alwasilah.edu.gh")
    address = models.CharField(max_length=255, default="Tamale, Ghana")
    footer_copyright = models.CharField(max_length=255, default="Copyright © 2026 Al-Wasilah School Complex. All rights reserved.")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    login_background = models.ImageField(upload_to='branding/', blank=True, null=True)

    def __str__(self):
        return self.school_name

class StudentProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    assigned_class = models.CharField(max_length=50, default="Primary 1")
    index_number = models.CharField(max_length=50, blank=True, null=True)
    generated_password = models.CharField(max_length=50, blank=True, null=True, default="123456")
    must_change_password = models.BooleanField(default=False)
    can_brand_portal = models.BooleanField(default=False)
    passport_picture = models.ImageField(upload_to='passports/', blank=True, null=True)
    days_present = models.IntegerField(default=0)
    total_school_days = models.IntegerField(default=60)
    conduct_rating = models.CharField(max_length=50, default="GOOD")
    teacher_remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class FeeLedger(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_entries')
    title = models.CharField(max_length=255, default="First Term School Fees")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    academic_year = models.CharField(max_length=50, default="2026/2027")
    date_recorded = models.DateTimeField(auto_now_add=True)

    @property
    def balance(self):
        return self.amount_due - self.amount_paid

class AcademicResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results')
    subject_name = models.CharField(max_length=100)
    class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    position_in_subject = models.CharField(max_length=20, blank=True, null=True)
    academic_term = models.CharField(max_length=50, default="Term 1")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_score(self):
        return self.class_score + self.exam_score

    @property
    def grade(self):
        tot = self.total_score
        if tot >= 80: return 'A'
        if tot >= 70: return 'B'
        if tot >= 60: return 'C'
        if tot >= 50: return 'D'
        return 'F'

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    target_role = models.CharField(max_length=50, default="all")
    date_posted = models.DateTimeField(auto_now_add=True)

class TimetableEntry(models.Model):
    class_name = models.CharField(max_length=50, default="Primary 1")
    day_of_week = models.CharField(max_length=20, default="Monday")
    period_time = models.CharField(max_length=50, default="08:00 - 08:45 AM")
    subject_name = models.CharField(max_length=100, default="Mathematics")
    teacher_name = models.CharField(max_length=100, default="Teacher")
    venue = models.CharField(max_length=100, default="Primary Block Room 1")