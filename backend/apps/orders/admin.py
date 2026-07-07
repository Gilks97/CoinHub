from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from .models import Order
from apps.core.constants import ORDER_PAID, ORDER_LOADED
from apps.accounts.models import Role

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Rearranged columns: Status -> Action -> Processed By -> Completed At
    list_display = (
        "reference",
        "coin_type",
        "app_user_id",
        "phone_number",
        "coins_requested",
        "amount_paid_display",
        "status_badge",
        "dispatch_action",  # The automated row button column
        "loaded_by",        # Shows who clicked it automatically
        "loaded_at",        # Shows exactly when it was clicked automatically
    )
    list_filter = ("status", "coin_type", "created_at")
    search_fields = ("reference", "app_user_id", "phone_number")
    ordering = ["-created_at"]
    
    actions = ["mark_as_loaded_action"]

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

    # ── Automated Inline Row Button ──────────────────────────────────────────

    def dispatch_action(self, obj):
        """
        Renders a clickable button. When clicked, it automatically captures
        the logged-in user, the current timestamp, and flips the status.
        """
        if obj.status == ORDER_PAID:
            return format_html(
                '<a class="button" href="{}/mark-loaded/" '
                'style="background-color: #27ae60; color: white; padding: 4px 12px; '
                'border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 11px; '
                'display: inline-block; text-align: center;">'
                'Ship Coins</a>',
                obj.id
            )
        elif obj.status == ORDER_LOADED:
            return format_html(
                '<span style="color: #2980b9; font-size: 11px; font-weight: bold;">'
                '✓ Dispatched</span>'
            )
        return format_html('<span style="color: #95a5a6; font-size: 11px;">—</span>')
        
    dispatch_action.short_description = "Action"  # Simplified column title

    # ── Automated URL Processing Hook ────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:order_id>/mark-loaded/',
                self.admin_site.admin_view(self.process_individual_load),
                name='order-mark-loaded',
            ),
        ]
        return custom_urls + urls

    def process_individual_load(self, request, order_id):
        """
        Fires automatically when 'Ship Coins' is clicked. Captures who 
        is logged in, logs the time, changes the status, and returns instantly.
        """
        try:
            order = Order.objects.get(pk=order_id)
            if order.status == ORDER_PAID:
                order.status = ORDER_LOADED
                order.loaded_at = timezone.now()  # Automatically picks up server time
                order.loaded_by = request.user    # Automatically picks up active Agent/Admin account
                order.loading_notes = f"Dispatched instantly via row action button by user: {request.user.username}."
                order.save()
                self.message_user(request, f"Order {order.reference} successfully dispatched.", level='success')
            else:
                self.message_user(request, "This order has already been processed or is unpaid.", level='warning')
        except Order.DoesNotExist:
            self.message_user(request, "Order not found.", level='error')
            
        return redirect('admin:orders_order_changelist')

    # ── Role-Based Permissions Logic ──────────────────────────────────────────

    def get_readonly_fields(self, request, obj=None):
        if hasattr(request.user, 'staff_profile') and request.user.staff_profile.role == Role.AGENT:
            return [f.name for f in Order._meta.fields] + ["created_at", "updated_at"]
        return ("reference", "coin_type", "app_user_id", "phone_number",
                "coins_requested", "amount_paid", "created_at", "updated_at")

    def has_change_permission(self, request, obj=None):
        return True

    # ── Bulk Dropdown Fallback Action ─────────────────────────────────────────

    def mark_as_loaded_action(self, request, queryset):
        paid_orders = queryset.filter(status=ORDER_PAID)
        count = paid_orders.count()
        if count == 0:
            self.message_user(request, "No eligible 'Paid' orders were selected.", level='warning')
            return

        for order in paid_orders:
            order.status = ORDER_LOADED
            order.loaded_at = timezone.now()
            order.loaded_by = request.user
            order.loading_notes = f"Manually processed via admin panel bulk action by {request.user.username}."
            order.save()

        self.message_user(request, f"Successfully marked {count} order(s) as Loaded.", level='success')

    mark_as_loaded_action.short_description = "Mark selected orders as Manually Loaded"

    # ── Visual Display Filters ────────────────────────────────────────────────

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