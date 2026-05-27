"""
CoinHub accounts — staff profiles and role-based permissions.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimestampedModel


class Role(models.TextChoices):
    SUPERADMIN = "superadmin", "SuperAdmin"
    AGENT = "agent", "Agent"


class StaffProfile(TimestampedModel):
    """
    Extends Django's built-in User with a CoinHub role.

    SuperAdmin: full CRUD, manage rates, manage users, mark loaded.
    Agent: view only — no create/edit/delete.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AGENT)
    phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        return self.role == Role.SUPERADMIN

    @property
    def is_agent(self):
        return self.role == Role.AGENT
