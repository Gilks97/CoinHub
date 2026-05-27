"""
Management command: create_default_superuser

Creates the superuser defined in .env if it doesn't already exist.
Safe to run on every container start (idempotent).

Usage:
    python manage.py create_default_superuser
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config


class Command(BaseCommand):
    help = "Create the default superuser from environment variables (idempotent)."

    def handle(self, *args, **options):
        username = config("DJANGO_SUPERUSER_USERNAME", default="admin")
        email = config("DJANGO_SUPERUSER_EMAIL", default="admin@coinhub.co.ke")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="changeme123!")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists — skipping."))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created successfully."))
