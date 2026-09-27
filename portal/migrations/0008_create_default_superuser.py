from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('portal', 'UserProfile')

    USERNAME = 'admin'
    PASSWORD = 'hananatubaA1'  # Ensure this is the password you want
    EMAIL = 'ahaqq861@gmail.com'

    if not User.objects.filter(username=USERNAME).exists():
        admin_user = User.objects.create(
            username=USERNAME,
            email=EMAIL,
            password=make_password(PASSWORD),
            is_staff=True,
            is_superuser=True,
            is_active=True,
            first_name='Portal',
            last_name='Admin'
        )

        # Create basic UserProfile without conflicting extra fields
        if not UserProfile.objects.filter(user=admin_user).exists():
            UserProfile.objects.create(
                user=admin_user,
                role='admin'
            )

def remove_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]