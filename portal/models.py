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
    date_recorded = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"