"""
CoinHub custom admin site — overrides index to inject dashboard stats cards.
"""
from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum, Count


class CoinHubAdminSite(admin.AdminSite):
    site_header = "CoinHub"
    site_title  = "CoinHub Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        from apps.orders.models import Order
        from apps.core.constants import ORDER_PAID, ORDER_PENDING

        today = timezone.now().date()
        month_start = today.replace(day=1)

        orders_today   = Order.objects.filter(created_at__date=today)
        orders_month   = Order.objects.filter(created_at__date__gte=month_start)

        stats = {
            "orders_today":   orders_today.count(),
            "paid_today":     orders_today.filter(status=ORDER_PAID).count(),
            "pending_today":  orders_today.filter(status=ORDER_PENDING).count(),
            "revenue_today":  orders_today.filter(status=ORDER_PAID).aggregate(
                                total=Sum("amount_paid"))["total"] or 0,
            "revenue_month":  orders_month.filter(status=ORDER_PAID).aggregate(
                                total=Sum("amount_paid"))["total"] or 0,
        }

        extra_context = extra_context or {}
        extra_context["coinhub_stats"] = stats
        return super().index(request, extra_context)
