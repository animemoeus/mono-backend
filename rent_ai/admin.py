from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Product, ProductCategory, ProductImage, ProductTag, Setting


@admin.register(ProductCategory)
class ProductCategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "original_id", "created_at", "updated_at")
    search_fields = ("name", "slug", "original_document_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ProductTag)
class ProductTagAdmin(ModelAdmin):
    list_display = ("name", "original_id", "created_at", "updated_at")
    search_fields = ("name", "original_document_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "name",
        "category",
        "slug",
        "weekly_price",
        "monthly_price",
        "show_product_in_store",
        "updated_at",
    )
    list_filter = ("show_product_in_store", "category")
    search_fields = ("name", "slug", "original_document_id", "stripe_product_id")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("tags", "addons")


@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product", "image_url", "created_at", "updated_at")
    search_fields = ("product__name", "image_url")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Setting)
class SettingAdmin(SingletonModelAdmin, ModelAdmin):
    actions_detail = ["sync_from_external_source"]
    readonly_fields = ("created_at", "updated_at")

    @action(
        description="Sync from external source",
        url_path="sync-from-external-source",
        permissions=["sync_from_external_source"],
    )
    def sync_from_external_source(self, request: HttpRequest, object_id: int):
        setting = Setting.get_solo()
        try:
            result = setting.update_from_external_source()
            level = messages.ERROR if result.startswith("Failed") or result.startswith("Invalid") else messages.SUCCESS
            self.message_user(request, result, level=level)
        except Exception as exc:
            self.message_user(request, f"Failed to sync data: {exc}", level=messages.ERROR)

        return redirect(reverse_lazy("admin:rent_ai_setting_change", args=(object_id,)))

    def has_sync_from_external_source_permission(self, request: HttpRequest, object_id):
        return request.user.is_staff
