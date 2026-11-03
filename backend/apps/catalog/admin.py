from django.contrib import admin
from .models import CoinType


@admin.register(CoinType)
class CoinTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price_per_1000", "conversion_rate", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("conversion_rate", "created_at", "updated_at")
    list_editable = ("active", "price_per_1000")
    actions = ["deactivate_selected", "activate_selected"]  

    # NEW: only superusers can delete coins (this also hides "Delete selected")
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # NEW: safe alternative to deleting; hides coins from the site but keeps history
    @admin.action(description="Hide selected coins from the site (deactivate)")
    def deactivate_selected(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f"{count} coin(s) deactivated.")

    @admin.action(description="Show selected coins on the site (activate)")
    def activate_selected(self, request, queryset):
        count = queryset.update(active=True)
        self.message_user(request, f"{count} coin(s) activated.")