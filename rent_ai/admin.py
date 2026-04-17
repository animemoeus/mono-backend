from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Product, ProductCategory, ProductImage, ProductTag, Setting
from .tasks import generate_product_embedding_task, generate_product_embeddings_task


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
    actions_detail = ["generate_embedding_detail"]
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
    exclude = ("embedding",)
    filter_horizontal = ("tags", "addons")

    @action(
        description="Generate embedding",
        url_path="generate-embedding",
        permissions=["generate_embedding_detail"],
    )
    def generate_embedding_detail(self, request: HttpRequest, object_id: int):
        product = self.get_object(request, object_id)
        if not product:
            self.message_user(request, "Product not found.", level=messages.ERROR)
            return redirect(reverse_lazy("admin:rent_ai_product_changelist"))

        try:
            generate_product_embedding_task.delay(product.id, True)
            self.message_user(request, f"Embedding queued for {product.name}.", level=messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Failed to queue embedding: {exc}", level=messages.ERROR)

        return redirect(reverse_lazy("admin:rent_ai_product_change", args=(object_id,)))

    def has_generate_embedding_detail_permission(self, request: HttpRequest, object_id):
        return request.user.is_staff

    @action(description="Generate embedding for selected products")
    def generate_embedding_selected(self, request, queryset):
        product_ids = list(queryset.values_list("id", flat=True))
        if not product_ids:
            self.message_user(request, "No product selected.", level=messages.WARNING)
            return

        try:
            generate_product_embeddings_task.delay(product_ids, True)
            self.message_user(
                request,
                f"Embedding queued for {len(product_ids)} product(s).",
                level=messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(request, f"Failed to queue embedding batch: {exc}", level=messages.ERROR)

    actions = ["generate_embedding_selected"]


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
