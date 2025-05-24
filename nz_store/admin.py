from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AccountStock, Product, ProductCategory, TelegramUser


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    autocomplete_fields = ("category",)
    list_display = ("name", "category", "price", "stock", "created_at", "updated_at")
    search_fields = ("name", "category__name")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("category",)


@admin.register(AccountStock)
class AccountStockAdmin(ModelAdmin):
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
    list_filter = ("is_sold",)


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    list_display = ("telegram_id", "username", "created_at", "updated_at")
    search_fields = ("telegram_id", "username")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("username",)
