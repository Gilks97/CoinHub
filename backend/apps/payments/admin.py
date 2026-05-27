from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order_ref",
        "phone_number",
        "amount_display",
        "status_badge",
        "mpesa_receipt",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order__reference", "phone_number", "mpesa_receipt", "checkout_request_id")
    readonly_fields = (
        "order", "checkout_request_id", "merchant_request_id",
        "mpesa_receipt", "phone_number", "amount", "status",
        "raw_callback_json", "created_at", "updated_at",
    )

    def order_ref(self, obj):
        return obj.order.reference
    order_ref.short_description = "Order Ref"

    def amount_display(self, obj):
        return f"KES {obj.amount:,.0f}"
    amount_display.short_description = "Amount"

    def status_badge(self, obj):
        colors = {
            "pending": "#f39c12",
            "success": "#27ae60",
            "failed": "#e74c3c",
            "cancelled": "#95a5a6",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:3px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Status"
