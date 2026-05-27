from django.contrib import admin
from django.utils.html import format_html
from .models import Order
from apps.core.constants import ORDER_PAID, ORDER_LOADED


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "coin_type",
        "app_user_id",
        "phone_number",
        "coins_requested",
        "amount_paid_display",
        "status_badge",
        "created_at",
    )
    list_filter = ("status", "coin_type", "created_at")
    search_fields = ("reference", "app_user_id", "phone_number")
    readonly_fields = ("reference", "coin_type", "app_user_id", "phone_number",
                       "coins_requested", "amount_paid", "created_at", "updated_at")
    ordering = ["-created_at"]

    fieldsets = (
        ("Order Details", {
            "fields": ("reference", "coin_type", "app_user_id", "phone_number",
                       "coins_requested", "amount_paid", "status"),
        }),
        ("Loading Info", {
            "fields": ("loaded_at", "loaded_by", "loading_notes"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def amount_paid_display(self, obj):
        return f"KES {obj.amount_paid:,.0f}"
    amount_paid_display.short_description = "Amount (KES)"

    def status_badge(self, obj):
        colors = {
            "pending": "#f39c12",
            "paid": "#27ae60",
            "loaded": "#2980b9",
            "failed": "#e74c3c",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:3px;font-size:11px">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = "Status"
