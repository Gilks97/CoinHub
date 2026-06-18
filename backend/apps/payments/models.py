from django.db import models
from apps.core.models import TimestampedModel
from apps.core.constants import PAYMENT_STATUS_CHOICES, PAYMENT_PENDING

class Payment(TimestampedModel):
    """
    Tracks the M-Pesa STK Push transaction for an Order with deep audit payloads.
    """
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment",
    )
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True, null=True)
    merchant_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True, db_index=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # ─── RECONCILIATION & AUDIT FIELDS ──────────────────────────────────────
    result_code = models.IntegerField(null=True, blank=True, help_text="Safaricom Response/Callback Result Code")
    result_description = models.TextField(null=True, blank=True)
    
    request_payload = models.JSONField(blank=True, null=True, help_text="Payload sent to Daraja API")
    response_payload = models.JSONField(blank=True, null=True, help_text="Immediate API response from Daraja")
    callback_payload = models.JSONField(blank=True, null=True, help_text="Final callback payload from Safaricom")
    callback_received_at = models.DateTimeField(blank=True, null=True)
    # ────────────────────────────────────────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
        db_index=True,
    )
    raw_callback_json = models.JSONField(null=True, blank=True)  # Backward compatibility

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment for {self.order.reference} — {self.status}"