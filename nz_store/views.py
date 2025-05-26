from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from .models import Product
from .pagination import ProductListPagination
from .serializers import ProductSerializer


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
