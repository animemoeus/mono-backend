from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.decorators import action

from .models import AccountStock, Product, ProductCategory, Settings, TelegramUser


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(SimpleHistoryAdmin, ModelAdmin):
    autocomplete_fields = ("category",)
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "category__name")
    readonly_fields = ("stock", "created_at", "updated_at")
    list_filter = (["category", AutocompleteSelectFilter], "is_active")
    ordering = ("name",)

    actions_detail = ["update_stock"]

    @action(description="Update Stock", icon="refresh")
    def update_stock(self, request, object_id):
        try:
            product = Product.objects.get(pk=object_id)
            product.sync_stock_with_accounts()
            self.message_user(request, "Stock updated successfully", level="success")
        except Product.DoesNotExist:
            self.message_user(request, "Product not found", level="error")

        return redirect(reverse_lazy("admin:nz_store_product_change", args=(object_id,)))


@admin.register(AccountStock)
class AccountStockAdmin(SimpleHistoryAdmin, ModelAdmin):
    autocomplete_fields = ("product",)
    list_display = (
        "product",
        "email",
        "username",
        "is_sold",
        "created_at",
        "updated_at",
    )
    search_fields = ("email", "username", "product__name")
    readonly_fields = ("created_at", "updated_at")
    list_filter = (["product", AutocompleteSelectFilter], "is_sold")
    ordering = ("-created_at",)


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    list_display = ("telegram_id", "username", "created_at", "updated_at")
    search_fields = ("telegram_id", "username")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("username",)


@admin.register(Settings)
class SettingsAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("bot_name", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request):
        """Prevent adding new settings, only allow editing the existing one."""
        return not Settings.objects.exists()
