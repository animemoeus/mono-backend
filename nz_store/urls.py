from django.urls import path

from .views import ProductCategoryListAPIView, ProductListAPIView

urlpatterns = [
    path("categories/", ProductCategoryListAPIView.as_view(), name="nz-category-list"),
    path("products/", ProductListAPIView.as_view(), name="nz-product-list"),
]

app_name = "nz_store"
