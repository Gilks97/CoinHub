import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order_ref",
        "phone_number",
        "amount_display",
        "status_badge",
        "mpesa_receipt",
        "result_code",
        "created_at",
    )
    
    list_filter = ("status", "created_at", "updated_at")
    
    search_fields = (
        "order__reference", 
        "phone_number", 
        "mpesa_receipt", 
        "checkout_request_id",
        "merchant_request_id"
    )
    
    # All fields locked out from manual editing to secure raw financial history
    readonly_fields = (
        "order",
        "checkout_request_id",
        "merchant_request_id",
        "mpesa_receipt",
        "phone_number",
        "amount",
        "status",
        "result_code",
        "result_description",
        "created_at", 
        "updated_at", 
        "callback_received_at",
        "pretty_request_payload", 
        "pretty_response_payload", 
        "pretty_callback_payload",
        "raw_callback_json",
    )
    
    ordering = ("-created_at",)

    fieldsets = (
        ("Core Transaction Details", {
            "fields": ("order", "status", "amount", "phone_number")
        }),
        ("M-Pesa Technical Identifiers", {
            "fields": (
                "mpesa_receipt", 
                "checkout_request_id", 
                "merchant_request_id", 
                ("result_code", "result_description"),
            )
        }),
        ("Timestamps & Windows", {
            "fields": ("created_at", "updated_at", "callback_received_at")
        }),
        ("Raw API Payloads (Debug Logs)", {
            "classes": ("collapse",),  
            "fields": (
                "pretty_request_payload", 
                "pretty_response_payload", 
                "pretty_callback_payload",
                "raw_callback_json",  
            ),
        }),
    )

    # ─── ORIGINAL CUSTOM DISPLAY HELPERS ────────────────────────────────────

    @admin.display(ordering="order__reference", description="Order Ref")
    def order_ref(self, obj):
        return obj.order.reference

    @admin.display(ordering="amount", description="Amount")
    def amount_display(self, obj):
        return f"KES {obj.amount:,.0f}"

    @admin.display(ordering="status", description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "#f39c12",
            "success": "#27ae60",
            "failed": "#e74c3c",
            "cancelled": "#95a5a6",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:3px;font-size:11px;font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    # ─── JSON RECONCILIATION VISUAL UTILITIES ───────────────────────────────────
    
    def _format_json_field(self, data):
        if not data:
            return mark_safe("<em style='color: #888;'>No data recorded yet.</em>")
        formatted = json.dumps(data, indent=4)
        return mark_safe(
            f"<pre style='background: #1e1e1e; color: #4af626; padding: 15px; "
            f"border-radius: 6px; font-family: monospace; overflow-x: auto; "
            f"max-height: 400px; border: 1px solid #333;'>{formatted}</pre>"
        )

    @admin.display(description="STK Request Sent")
    def pretty_request_payload(self, obj):
        return self._format_json_field(obj.request_payload)

    @admin.display(description="Safaricom Handshake Response")
    def pretty_response_payload(self, obj):
        return self._format_json_field(obj.response_payload)

    @admin.display(description="Final Callback Received")
    def pretty_callback_payload(self, obj):
        return self._format_json_field(obj.callback_payload)