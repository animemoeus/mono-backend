from rest_framework.generics import ListAPIView

from .models import Product
from .pagination import ProductListPagination
from .serializers import ProductSerializer


class ProductListView(ListAPIView):
    """
    API endpoint to get all NZ products with pagination.
    """

    queryset = Product.objects.select_related("category").filter(is_active=True)
    serializer_class = ProductSerializer
    pagination_class = ProductListPagination
