from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from nz_store.tests.factories import ProductCategoryFactory, ProductFactory


class ProductDetailViewTestCase(APITestCase):
    """Test cases for ProductDetailAPIView endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create category
        self.category = ProductCategoryFactory(name="Electronics")

        # Create active product
        self.product = ProductFactory(
            name="Smartphone",
            category=self.category,
            price=Decimal("999.99"),
            stock=10,
            is_active=True,
        )

        # Create inactive product (should not be accessible)
        self.inactive_product = ProductFactory(
            name="Inactive Product",
            category=self.category,
            price=Decimal("100.00"),
            stock=5,
            is_active=False,
        )

    def test_get_product_detail_success(self):
        """Test successful retrieval of product detail."""
        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": self.product.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uuid"], str(self.product.uuid))
        self.assertEqual(response.data["name"], self.product.name)
        self.assertEqual(response.data["description"], self.product.description)
        self.assertEqual(Decimal(response.data["price"]), self.product.price)
        self.assertEqual(response.data["stock"], self.product.stock)
        self.assertEqual(response.data["available_stock"], self.product.available_stock)
        self.assertEqual(response.data["is_active"], self.product.is_active)

        # Check category data
        self.assertEqual(response.data["category"]["uuid"], str(self.category.uuid))
        self.assertEqual(response.data["category"]["name"], self.category.name)
        self.assertEqual(response.data["category"]["description"], self.category.description)

        # Check timestamps are present
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_get_product_detail_not_found(self):
        """Test getting product detail with non-existent UUID."""
        from uuid import uuid4

        non_existent_uuid = uuid4()
        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": non_existent_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_inactive_product_detail_not_found(self):
        """Test that inactive products are not accessible via detail endpoint."""
        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": self.inactive_product.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product_detail_invalid_uuid_format(self):
        """Test getting product detail with invalid UUID format."""
        # Django's UUID converter will reject invalid UUID formats before
        # reaching the view, resulting in a 404 from URL routing
        invalid_url = "/nz-store/products/invalid-uuid-format/"
        response = self.client.get(invalid_url)

        # This will return 404 because the URL pattern doesn't match invalid UUID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_detail_response_structure(self):
        """Test that the response has the expected structure."""
        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": self.product.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that all expected fields are present
        expected_fields = {
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
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

        # Check category nested structure
        category_expected_fields = {"uuid", "name", "description", "product_count"}
        self.assertEqual(set(response.data["category"].keys()), category_expected_fields)

    def test_product_with_image_detail(self):
        """Test product detail response when product has an image."""
        # The factory already creates an image, so we just need to verify it's included
        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": self.product.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["image"])
        # self.assertTrue(response.data["image"].startswith("/media/"))

    def test_product_without_image_detail(self):
        """Test product detail response when product has no image."""
        # Create a product without an image
        product_without_image = ProductFactory(
            name="Product Without Image",
            category=self.category,
            image=None,
            is_active=True,
        )

        url = reverse("nz-store:nz-product-detail", kwargs={"uuid": product_without_image.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["image"])
