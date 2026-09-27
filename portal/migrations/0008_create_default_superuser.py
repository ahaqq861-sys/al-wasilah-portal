from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('portal', 'UserProfile')

    # Define your live admin credentials here
    USERNAME = 'admin'
    PASSWORD = 'hananatubaA1'  # Change this to your preferred password
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

        # Create corresponding admin profile if UserProfile model exists
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'index_number': 'ADMIN001',
                'programme': 'ADMINISTRATION',
                'assigned_class': 'N/A'
            }
        )

def remove_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),  # Make sure this matches your previous migration name
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]