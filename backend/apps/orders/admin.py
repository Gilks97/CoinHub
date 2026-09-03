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
    list_display = (
        "reference",
        "coin_type",
        "app_user_id",
        "phone_number",
        "coins_requested",
        "amount_paid_display",
        "status_badge",
        "dispatch_action",
        "loaded_by",
        "loaded_at",
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

    # ── Mobile Responsive CSS Injector ────────────────────────────────────────

    class Media:
        css = {
            "all": ("admin/css/mobile_orders_cards.css",)
        }

    def changelist_view(self, request, extra_context=None):
        """
        Injects mobile-first CSS directly into the changelist head without 
        requiring static file collection rebuilds during rapid iteration.
        """
        extra_context = extra_context or {}
        extra_context["mobile_card_styles"] = format_html("""
            <style>
                @media (max-width: 768px) {
                    /* Hide standard table headers */
                    #result_list thead { display: none !important; }
                    
                    /* Convert Table into vertical Card Stack */
                    #result_list, #result_list tbody, #result_list tr, #result_list td {
                        display: block !important;
                        width: 100% !important;
                        box-sizing: border-box !important;
                    }

                    /* Style individual Order Rows as Mobile Cards */
                    #result_list tr {
                        background: #ffffff !important;
                        margin-bottom: 16px !important;
                        border-radius: 12px !important;
                        border: 1px solid #e2e8f0 !important;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
                        padding: 14px !important;
                        position: relative !important;
                    }

                    #result_list tr:nth-child(even) { background: #ffffff !important; }

                    /* Target each table cell */
                    #result_list td {
                        border: none !important;
                        padding: 6px 0 !important;
                        text-align: left !important;
                        font-size: 13px !important;
                    }

                    /* Header Info: Reference + Status Badge on same line */
                    #result_list td.field-reference {
                        font-size: 16px !important;
                        font-weight: 700 !important;
                        color: #1e293b !important;
                        border-bottom: 1px solid #f1f5f9 !important;
                        padding-bottom: 8px !important;
                        margin-bottom: 8px !important;
                    }

                    /* Full-width thumb-friendly Ship Coins button */
                    #result_list td.field-dispatch_action {
                        margin-top: 10px !important;
                        padding-top: 10px !important;
                        border-top: 1px dashed #e2e8f0 !important;
                    }

                    #result_list td.field-dispatch_action a.button {
                        display: block !important;
                        width: 100% !important;
                        padding: 12px 0 !important;
                        font-size: 14px !important;
                        text-align: center !important;
                        border-radius: 8px !important;
                        box-shadow: 0 2px 4px rgba(39, 174, 96, 0.2) !important;
                    }

                    /* Select Checkbox adjustment */
                    #result_list td.action-checkbox {
                        position: absolute !important;
                        top: 12px !important;
                        right: 12px !important;
                        width: auto !important;
                    }
                }
            </style>
        """)
        return super().changelist_view(request, extra_context=extra_context)

    # ── Automated Inline Row Button ──────────────────────────────────────────

    def dispatch_action(self, obj):
        if obj.status == ORDER_PAID:
            return format_html(
                '<a class="button" href="{}/mark-loaded/" '
                'style="background-color: #27ae60; color: white; padding: 6px 16px; '
                'border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 12px; '
                'display: inline-block; text-align: center; transition: all 0.2s;">'
                '🚀 Ship Coins</a>',
                obj.id
            )
        elif obj.status == ORDER_LOADED:
            return format_html(
                '<div style="color: #27ae60; font-size: 12px; font-weight: 700; background: #e8f8f0; '
                'padding: 6px 12px; border-radius: 6px; text-align: center;">'
                '✓ Dispatched</div>'
            )
        return format_html('<span style="color: #95a5a6; font-size: 12px;">—</span>')
        
    dispatch_action.short_description = "Action"

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
        try:
            order = Order.objects.get(pk=order_id)
            if order.status == ORDER_PAID:
                order.status = ORDER_LOADED
                order.loaded_at = timezone.now()
                order.loaded_by = request.user
                order.loading_notes = f"Dispatched via mobile card action by user: {request.user.username}."
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
    amount_paid_display.short_description = "Amount"

    def status_badge(self, obj):
        colors = {
            "pending": "#f39c12",
            "paid": "#27ae60",
            "loaded": "#2980b9",
            "failed": "#e74c3c",
        }
        color = colors.get(obj.status, "#95a5a6")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:bold;display:inline-block;">{}</span>',
            color,
            obj.get_status_display().upper(),
        )
    status_badge.short_description = "Status"