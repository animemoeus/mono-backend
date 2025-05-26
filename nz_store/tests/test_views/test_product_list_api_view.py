from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from nz_store.tests.factories import ProductCategoryFactory, ProductFactory


class ProductListViewTestCase(APITestCase):
    """Test cases for ProductListView API endpoint."""

    def setUp(self):
        """Set up test data."""
        # Create categories
        self.category1 = ProductCategoryFactory(name="Electronics")
        self.category2 = ProductCategoryFactory(name="Books")

        # Create active products
        self.product1 = ProductFactory(
            name="Smartphone",
            category=self.category1,
            price=Decimal("999.99"),
            stock=10,
            is_active=True,
        )
        self.product2 = ProductFactory(
            name="Laptop",
            category=self.category1,
            price=Decimal("1299.99"),
            stock=5,
            is_active=True,
        )
        self.product3 = ProductFactory(
            name="Programming Book",
            category=self.category2,
            price=Decimal("59.99"),
            stock=20,
            is_active=True,
        )

        # Create inactive product (should not appear in results)
        self.inactive_product = ProductFactory(
            name="Inactive Product",
            category=self.category1,
            price=Decimal("100.00"),
            stock=5,
            is_active=False,
        )

        self.url = reverse("nz_store:nz-product-list")

    def test_get_product_list_success(self):
        """Test that the API returns a list of active products."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check pagination structure
        self.assertIn("results", data)
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)

        # Should return 3 active products (inactive product excluded)
        self.assertEqual(data["count"], 3)
        self.assertEqual(len(data["results"]), 3)

        # Check product data structure
        product_data = data["results"][0]
        expected_fields = [
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
        for field in expected_fields:
            self.assertIn(field, product_data)

        # Check category structure
        category_data = product_data["category"]
        self.assertIn("uuid", category_data)
        self.assertIn("name", category_data)

    def test_products_ordered_by_created_at_desc(self):
        """Test that products are ordered by created_at in descending order."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        products = data["results"]

        # Check that products are ordered by created_at descending
        for i in range(len(products) - 1):
            current_date = products[i]["created_at"]
            next_date = products[i + 1]["created_at"]
            self.assertGreaterEqual(current_date, next_date)

    def test_filter_by_category_uuid(self):
        """Test filtering products by category UUID."""
        response = self.client.get(self.url, {"category__uuid": str(self.category1.uuid)})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 2 products from category1 (excluding inactive)
        self.assertEqual(data["count"], 2)

        # All products should belong to category1
        for product in data["results"]:
            self.assertEqual(product["category"]["uuid"], str(self.category1.uuid))

    def test_filter_by_category_name(self):
        """Test filtering products by category name."""
        response = self.client.get(self.url, {"category__name": "Books"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 1 product from Books category
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["category"]["name"], "Books")

    def test_search_by_product_name(self):
        """Test searching products by name."""
        response = self.client.get(self.url, {"search": "Smartphone"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 1 product matching "Smartphone"
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Smartphone")

    def test_search_by_category_name(self):
        """Test searching products by category name."""
        response = self.client.get(self.url, {"search": "Electronics"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 2 products from Electronics category (excluding inactive)
        self.assertEqual(data["count"], 2)
        for product in data["results"]:
            self.assertEqual(product["category"]["name"], "Electronics")

    def test_ordering_by_price_asc(self):
        """Test ordering products by price in ascending order."""
        response = self.client.get(self.url, {"ordering": "price"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        products = data["results"]

        # Check that products are ordered by price ascending
        for i in range(len(products) - 1):
            current_price = Decimal(products[i]["price"])
            next_price = Decimal(products[i + 1]["price"])
            self.assertLessEqual(current_price, next_price)

    def test_ordering_by_price_desc(self):
        """Test ordering products by price in descending order."""
        response = self.client.get(self.url, {"ordering": "-price"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        products = data["results"]

        # Check that products are ordered by price descending
        for i in range(len(products) - 1):
            current_price = Decimal(products[i]["price"])
            next_price = Decimal(products[i + 1]["price"])
            self.assertGreaterEqual(current_price, next_price)

    def test_ordering_by_name(self):
        """Test ordering products by name."""
        response = self.client.get(self.url, {"ordering": "name"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        products = data["results"]

        # Check that products are ordered by name ascending
        for i in range(len(products) - 1):
            current_name = products[i]["name"]
            next_name = products[i + 1]["name"]
            self.assertLessEqual(current_name, next_name)

    def test_pagination_default_page_size(self):
        """Test default pagination page size."""
        # Create more products to test pagination
        for i in range(25):  # Total will be 28 products (3 existing + 25 new)
            ProductFactory(name=f"Product {i}", category=self.category1, is_active=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 20 products (default page size)
        self.assertEqual(len(data["results"]), 20)
        self.assertEqual(data["count"], 28)  # Total count should be 28
        self.assertIsNotNone(data["next"])  # Should have next page
        self.assertIsNone(data["previous"])  # First page has no previous

    def test_pagination_custom_page_size(self):
        """Test custom page size using count parameter."""
        response = self.client.get(self.url, {"count": "2"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 2 products
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["count"], 3)  # Total count should be 3
        self.assertIsNotNone(data["next"])  # Should have next page

    def test_pagination_max_page_size_limit(self):
        """Test that page size is limited to max_page_size."""
        response = self.client.get(self.url, {"count": "200"})  # Request more than max

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return only 3 products (all available) even though we requested 200
        self.assertEqual(len(data["results"]), 3)

    def test_inactive_products_excluded(self):
        """Test that inactive products are excluded from results."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check that no inactive products are returned
        for product in data["results"]:
            self.assertTrue(product["is_active"])

        # Ensure inactive product is not in results
        product_names = [p["name"] for p in data["results"]]
        self.assertNotIn("Inactive Product", product_names)

    def test_combined_filters_and_search(self):
        """Test combining filters and search parameters."""
        response = self.client.get(
            self.url,
            {"category__name": "Electronics", "search": "Laptop", "ordering": "-price"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should return 1 product (Laptop from Electronics category)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["name"], "Laptop")
        self.assertEqual(data["results"][0]["category"]["name"], "Electronics")

    def test_empty_results(self):
        """Test API response when no products match the filters."""
        response = self.client.get(self.url, {"search": "NonExistentProduct"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["count"], 0)
        self.assertEqual(len(data["results"]), 0)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])
