from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Product, ProductCategory


class ProductCategorySerializer(ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            "uuid",
            "name",
            "description",
            "product_count",
        ]

    def get_product_count(self, obj):
        """Return the count of active products in this category."""
        # Use the annotated count from the queryset if available, otherwise query the database
        if hasattr(obj, "product_count"):
            return obj.product_count
        return obj.products.filter(is_active=True).count()


class ProductSerializer(ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    available_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "description",
            "image",
            "price",
            "stock",
            "available_stock",
            "is_active",
            "category",
            "created_at",
            "updated_at",
        ]
