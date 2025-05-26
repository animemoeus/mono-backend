from django.urls import path

from .views import ProductListAPIView

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="nz-product-list"),
]

app_name = "nz_store"
