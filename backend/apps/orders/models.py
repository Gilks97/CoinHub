"""
CoinHub orders — Order model.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimestampedModel
from apps.core.constants import ORDER_STATUS_CHOICES, ORDER_PENDING
from apps.catalog.models import CoinType


class Order(TimestampedModel):
    """
    Represents a single coin recharge request.

    Lifecycle: pending → paid → loaded
    Loading is manual, performed outside CoinHub by an administrator.
    """

    reference = models.CharField(max_length=20, unique=True, db_index=True)
    coin_type = models.ForeignKey(CoinType, on_delete=models.PROTECT, related_name="orders")
    app_user_id = models.CharField(max_length=100, help_text="External game/app user identifier")
    phone_number = models.CharField(max_length=20, help_text="M-Pesa phone in 2547XXXXXXXX format")
    coins_requested = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount in KES")
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default=ORDER_PENDING,
        db_index=True,
    )
    # Loading fields — updated manually by admin
    loaded_at = models.DateTimeField(null=True, blank=True)
    loaded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="loaded_orders",
    )
    loading_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.coin_type.name} ({self.status})"
