from django.urls import path

from .views import ProductCategoryListAPIView, ProductDetailAPIView, ProductListAPIView

urlpatterns = [
    path("categories/", ProductCategoryListAPIView.as_view(), name="nz-category-list"),
    path("products/", ProductListAPIView.as_view(), name="nz-product-list"),
    path(
        "products/<uuid:uuid>/",
        ProductDetailAPIView.as_view(),
        name="nz-product-detail",
    ),
]

app_name = "nz_store"
