from django.contrib import admin
from .models import CoinType


@admin.register(CoinType)
class CoinTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "conversion_rate", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("active", "conversion_rate")
