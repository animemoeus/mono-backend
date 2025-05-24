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

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "description",
            "image",
            "price",
            "stock",
            "category",
            "created_at",
            "updated_at",
        ]
