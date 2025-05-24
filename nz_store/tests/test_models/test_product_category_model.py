import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from nz_store.models import ProductCategory
from nz_store.tests.factories import ProductCategoryFactory, ProductFactory


class ProductCategoryModelTest(TestCase):
    """Test case for ProductCategory model."""

    def setUp(self):
        """Set up test data."""
        self.category = ProductCategoryFactory(
            name="Gaming Accounts",
            description="Premium gaming accounts for various platforms",
        )

    def test_product_category_creation(self):
        """Test ProductCategory model creation."""
        self.assertIsInstance(self.category, ProductCategory)
        self.assertEqual(self.category.name, "Gaming Accounts")
        self.assertEqual(self.category.description, "Premium gaming accounts for various platforms")
        self.assertIsNotNone(self.category.uuid)
        self.assertIsNotNone(self.category.created_at)
        self.assertIsNotNone(self.category.updated_at)

    def test_product_category_str_representation(self):
        """Test the string representation of ProductCategory."""
        self.assertEqual(str(self.category), "Gaming Accounts")

    def test_product_category_uuid_field(self):
        """Test that UUID field is properly generated and unique."""
        # Check that UUID is valid
        self.assertIsInstance(self.category.uuid, uuid.UUID)

        # Create another category and check UUID uniqueness
        category2 = ProductCategoryFactory(name="Social Media Accounts")
        self.assertNotEqual(self.category.uuid, category2.uuid)

    def test_product_category_name_field(self):
        """Test ProductCategory name field properties."""
        # Test max length
        long_name = "A" * 256  # Exceeds max_length of 255
        category = ProductCategory(name=long_name, description="Test description")

        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_product_category_description_field(self):
        """Test ProductCategory description field properties."""
        # Test that description can be blank
        category = ProductCategory(name="Test Category")
        category.full_clean()  # Should not raise validation error

        # Test that description can be null
        category_null_desc = ProductCategoryFactory(name="Test Category 2", description=None)
        self.assertIsNone(category_null_desc.description)

    def test_product_category_timestamps(self):
        """Test created_at and updated_at timestamps."""
        # Test that timestamps are set on creation
        self.assertIsNotNone(self.category.created_at)
        self.assertIsNotNone(self.category.updated_at)

        # Test that updated_at changes when model is saved
        original_updated_at = self.category.updated_at
        self.category.name = "Updated Gaming Accounts"
        self.category.save()

        self.assertNotEqual(original_updated_at, self.category.updated_at)
        self.assertGreater(self.category.updated_at, original_updated_at)

    def test_product_category_related_products(self):
        """Test the relationship between ProductCategory and Products."""
        # Create products for the category
        product1 = ProductFactory(category=self.category, name="Steam Account")
        product2 = ProductFactory(category=self.category, name="Epic Games Account")

        # Test the reverse relationship
        products = self.category.products.all()
        self.assertEqual(products.count(), 2)
        self.assertIn(product1, products)
        self.assertIn(product2, products)

    def test_product_category_deletion_cascade(self):
        """Test that deleting a category cascades to related products."""
        # Create a product for the category
        product = ProductFactory(category=self.category, name="Test Account")
        product_id = product.id

        # Delete the category
        self.category.delete()

        # Check that the product was also deleted
        from nz_store.models import Product

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=product_id)

    def test_product_category_factory_creation(self):
        """Test that ProductCategoryFactory creates valid instances."""
        category = ProductCategoryFactory()

        self.assertIsInstance(category, ProductCategory)
        self.assertIsNotNone(category.name)
        self.assertIsNotNone(category.uuid)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_product_category_factory_with_custom_values(self):
        """Test ProductCategoryFactory with custom values."""
        custom_name = "Custom Category Name"
        custom_description = "This is a custom description for testing"

        category = ProductCategoryFactory(name=custom_name, description=custom_description)

        self.assertEqual(category.name, custom_name)
        self.assertEqual(category.description, custom_description)

    def test_product_category_django_get_or_create(self):
        """Test that factory uses django_get_or_create for name field."""
        # First creation
        category1 = ProductCategoryFactory(name="Unique Category")

        # Second creation with same name should return the same object
        category2 = ProductCategoryFactory(name="Unique Category")

        self.assertEqual(category1.id, category2.id)
        self.assertEqual(category1.uuid, category2.uuid)
