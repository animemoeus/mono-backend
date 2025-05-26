from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from .models import Product, ProductCategory
from .pagination import CategoryListPagination, ProductListPagination
from .serializers import ProductCategorySerializer, ProductSerializer


class ProductCategoryListAPIView(ListAPIView):
    """
    API endpoint to get all NZ product categories.
    """

    queryset = ProductCategory.objects.all().annotate(
        product_count=models.Count("products", filter=models.Q(products__is_active=True))
    )

    serializer_class = ProductCategorySerializer
    pagination_class = CategoryListPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]


class ProductListAPIView(ListAPIView):
    """
    API endpoint to get all NZ products with pagination.
    """

    queryset = Product.objects.select_related("category").filter(is_active=True)
    serializer_class = ProductSerializer
    pagination_class = ProductListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category__uuid", "category__name"]
    search_fields = ["name", "category__name"]
    ordering_fields = ["created_at", "price", "name"]
    ordering = ["-created_at"]
