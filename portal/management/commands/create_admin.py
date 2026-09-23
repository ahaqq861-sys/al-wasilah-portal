import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Creates a superuser automatically on deployment if none exists."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "alwasilaschool2026@gmail.com")
        password = os.environ.get("ADMIN_PASSWORD", "Alwasilah2026!")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Successfully created superuser '{username}'."))
        else:
            self.stdout.write(self.style.NOTICE(f"Superuser '{username}' already exists."))