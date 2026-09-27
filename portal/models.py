import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PortalBranding(models.Model):
    school_name = models.CharField(max_length=255, default="Al-Wasilah School Complex")
    contact_email = models.EmailField(default="info@alwasilah.edu")
    contact_phone = models.CharField(max_length=50, default="+233 000 000 000")
    address = models.TextField(default="Tamale, Ghana")
    logo = models.ImageField(upload_to='branding/', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    index_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Personal & Demographic details
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    disability_status = models.CharField(max_length=255, default="None")
    passport_picture = models.ImageField(upload_to='passports/', null=True, blank=True)
    
    # Class & Program
    assigned_class = models.CharField(max_length=100, default="Primary 1")
    programme = models.CharField(max_length=100, default="General Studies")
    
    # Password tracking & Permissions
    must_change_password = models.BooleanField(default=True)
    can_brand_portal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role.upper()})"


class StudentResult(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='results')
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100)
    class_score = models.FloatField(default=0.0)
    exam_score = models.FloatField(default=0.0)
    total_score = models.FloatField(default=0.0)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.CharField(max_length=255, blank=True)
    academic_term = models.CharField(max_length=50, default="Term 1")
    academic_year = models.CharField(max_length=20, default="2026/2027")

    def save(self, *args, **kwargs):
        self.total_score = float(self.class_score) + float(self.exam_score)
        if self.total_score >= 80: self.grade = 'A'
        elif self.total_score >= 70: self.grade = 'B'
        elif self.total_score >= 60: self.grade = 'C'
        elif self.total_score >= 50: self.grade = 'D'
        else: self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject}"


class FeeLedgerEntry(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='fee_entries')
    title = models.CharField(max_length=200, default="School Fees")
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_recorded = models.DateField(auto_now_add=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.balance = float(self.amount_due) - float(self.amount_paid)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - Fees ({self.amount_paid})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'role': 'admin' if instance.is_superuser else 'student',
                'index_number': instance.username,
                'must_change_password': False if instance.is_superuser else True
            }
        )