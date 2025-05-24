from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Product, ProductCategory


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            "uuid",
            "name",
        ]


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
