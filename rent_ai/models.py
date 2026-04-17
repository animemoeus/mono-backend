from urllib.parse import urljoin

import requests
from django.db import models, transaction
from pgvector.django import VectorField
from solo.models import SingletonModel


class ProductCategory(models.Model):
    original_id = models.IntegerField(unique=True)
    original_document_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    original_id = models.IntegerField(unique=True)
    original_document_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, related_name="products", on_delete=models.CASCADE)
    tags = models.ManyToManyField(ProductTag, related_name="products", blank=True)

    addons = models.ManyToManyField("self", symmetrical=False, related_name="parent_products", blank=True)

    original_id = models.IntegerField(unique=True)
    original_document_id = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    short_description = models.TextField(blank=True)
    stripe_product_id = models.CharField(max_length=255, blank=True)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    show_product_in_store = models.BooleanField(default=False)

    weekly_price = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    setup_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    embedding = VectorField(dimensions=1536, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_embedding_text(self):
        tag_names = ", ".join(self.tags.order_by("name").values_list("name", flat=True))
        parts = [
            self.name,
            self.short_description,
            self.description,
            self.category.name if self.category_id else "",
            tag_names,
        ]
        return "\n".join(part for part in parts if part).strip()

    def generate_embedding(self, force=False):
        if self.embedding is not None and not force:
            return self.embedding

        text = self.get_embedding_text()
        if not text:
            raise ValueError("Product has no text content for embedding.")

        from backend.utils.openai import get_embedding

        self.embedding = get_embedding(text)
        self.save(update_fields=["embedding"])
        return self.embedding

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Setting(SingletonModel):
    class Meta:
        verbose_name = "Rent AI Setting"

    data_source_url = models.URLField(blank=True, max_length=5000)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def _to_decimal(value, default=0):
        if value in (None, ""):
            return default
        return value

    def _upsert_category(self, product_payload):
        category_data = product_payload.get("product_categories", {}).get("data", [])
        if not category_data:
            return None

        category = category_data[0]
        attributes = category.get("attributes", {})
        category_obj, _ = ProductCategory.objects.update_or_create(
            original_id=category.get("id"),
            defaults={
                "original_document_id": category.get("documentId", ""),
                "name": attributes.get("name", "Uncategorized"),
                "slug": attributes.get("slug", f"category-{category.get('id')}"),
            },
        )
        return category_obj

    def _upsert_tags(self, product_payload):
        tags = []
        tag_data = product_payload.get("product_tags", {}).get("data", [])
        for tag in tag_data:
            attributes = tag.get("attributes", {})
            tag_obj, _ = ProductTag.objects.update_or_create(
                original_id=tag.get("id"),
                defaults={
                    "original_document_id": tag.get("documentId", ""),
                    "name": attributes.get("name", f"tag-{tag.get('id')}"),
                },
            )
            tags.append(tag_obj)
        return tags

    def _sync_product_images(self, product_obj, product_payload):
        image_data = product_payload.get("images", {}).get("data", [])
        desired_urls = set()

        for image in image_data:
            relative_url = image.get("attributes", {}).get("url")
            if not relative_url:
                continue
            image_url = urljoin(self.data_source_url, relative_url)
            desired_urls.add(image_url)
            ProductImage.objects.update_or_create(
                product=product_obj,
                image_url=image_url,
                defaults={},
            )

        if desired_urls:
            ProductImage.objects.filter(product=product_obj).exclude(image_url__in=desired_urls).delete()

    @staticmethod
    def _extract_product_addon_ids(product_payload):
        addon_product_ids = []
        addon_data = product_payload.get("addons", [])
        for addon in addon_data:
            addon_product = addon.get("product", {}).get("data", {})
            addon_id = addon_product.get("id")
            if addon_id:
                addon_product_ids.append(addon_id)
        return addon_product_ids

    def update_from_external_source(self):
        if not self.data_source_url:
            return "Data source URL is not set."

        try:
            response = requests.get(self.data_source_url, timeout=30)
            response.raise_for_status()
            payload = response.json()
            products = payload.get("data", [])

            if not isinstance(products, list):
                return "Invalid payload format from data source."

            synced_products = []
            pending_addons = {}

            with transaction.atomic():
                for product in products:
                    attributes = product.get("attributes", {})

                    if not product.get("id") or not attributes.get("slug"):
                        continue

                    category = self._upsert_category(attributes)
                    if not category:
                        continue

                    product_obj, _ = Product.objects.update_or_create(
                        original_id=product.get("id"),
                        defaults={
                            "category": category,
                            "original_document_id": product.get("documentId", ""),
                            "slug": attributes.get("slug", ""),
                            "name": attributes.get("name", ""),
                            "description": attributes.get("description") or "",
                            "short_description": attributes.get("short_description") or "",
                            "stripe_product_id": attributes.get("stripe_product_id") or "",
                            "security_deposit": self._to_decimal(attributes.get("security_deposit"), 0),
                            "show_product_in_store": attributes.get("show_product_in_store", False),
                            "weekly_price": self._to_decimal(attributes.get("weekly_price"), 0),
                            "monthly_price": self._to_decimal(attributes.get("monthly_price"), 0),
                            "monthly_discount_percentage": self._to_decimal(
                                attributes.get(
                                    "monthly_discount_percentage", attributes.get("monthly_discount_percent")
                                ),
                                0,
                            ),
                            "setup_cost": self._to_decimal(attributes.get("setup_cost"), 0),
                        },
                    )

                    tags = self._upsert_tags(attributes)
                    product_obj.tags.set(tags)
                    self._sync_product_images(product_obj, attributes)

                    pending_addons[product_obj.original_id] = self._extract_product_addon_ids(attributes)
                    synced_products.append(product_obj)

                for product_obj in synced_products:
                    addon_original_ids = pending_addons.get(product_obj.original_id, [])
                    addon_qs = Product.objects.filter(original_id__in=addon_original_ids)
                    product_obj.addons.set(addon_qs)

            return f"Data updated successfully. Synced {len(synced_products)} products."
        except requests.RequestException as e:
            return f"Failed to fetch data: {e}"
