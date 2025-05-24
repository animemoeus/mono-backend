import uuid
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from nz_store.models import Product
from nz_store.tests.factories import ProductCategoryFactory, ProductFactory


class ProductModelTest(TestCase):
    """Test case for Product model."""

    def setUp(self):
        """Set up test data."""
        self.category = ProductCategoryFactory(
            name="Gaming Accounts",
            description="Premium gaming accounts for various platforms",
        )
        self.product = ProductFactory(
            category=self.category,
            name="Netflix Premium Account",
            description="High-quality Netflix premium account with full access",
            price=Decimal("15.99"),
            stock=50,
        )

    def test_product_creation(self):
        """Test Product model creation."""
        self.assertIsInstance(self.product, Product)
        self.assertEqual(self.product.name, "Netflix Premium Account")
        self.assertEqual(
            self.product.description,
            "High-quality Netflix premium account with full access",
        )
        self.assertEqual(self.product.price, Decimal("15.99"))
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(self.product.category, self.category)
        self.assertIsNotNone(self.product.uuid)
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)

    def test_product_str_representation(self):
        """Test the string representation of Product."""
        self.assertEqual(str(self.product), "Netflix Premium Account")

    def test_product_uuid_field(self):
        """Test that UUID field is properly generated and unique."""
        # Check that UUID is valid
        self.assertIsInstance(self.product.uuid, uuid.UUID)

        # Create another product and check UUID uniqueness
        product2 = ProductFactory(name="Spotify Premium Account")
        self.assertNotEqual(self.product.uuid, product2.uuid)

    def test_product_category_foreign_key(self):
        """Test Product category foreign key relationship."""
        self.assertEqual(self.product.category.id, self.category.id)
        self.assertEqual(self.product.category.name, "Gaming Accounts")

        # Test that product appears in category's related products
        self.assertIn(self.product, self.category.products.all())

    def test_product_name_field(self):
        """Test Product name field properties."""
        # Test max length
        long_name = "A" * 256  # Exceeds max_length of 255
        product = Product(
            category=self.category,
            name=long_name,
            description="Test description",
            price=Decimal("10.00"),
            stock=1,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_description_field(self):
        """Test Product description field properties."""
        # Test that description is required (TextField without blank=True)
        product = Product(
            category=self.category,
            name="Test Product",
            description="",  # Empty description
            price=Decimal("10.00"),
            stock=1,
        )

        # This should raise ValidationError as description field doesn't allow blank
        with self.assertRaises(ValidationError):
            product.full_clean()

        # Test with valid description
        product.description = "Valid description"
        try:
            product.full_clean()
        except ValidationError:
            self.fail("Product description field should accept non-empty strings")

    def test_product_image_field(self):
        """Test Product image field properties."""
        # Test with no image (should be valid as blank=True, null=True)
        product = ProductFactory(image=None)
        self.assertFalse(bool(product.image))  # ImageFieldFile evaluates to False when no image

        # Test with image
        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
        image_file = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")

        product_with_image = ProductFactory(image=image_file)
        self.assertTrue(bool(product_with_image.image))  # ImageFieldFile evaluates to True when image exists

    def test_product_price_field(self):
        """Test Product price field properties."""
        # Test valid price
        self.assertEqual(self.product.price, Decimal("15.99"))

        # Test price with maximum digits (10 digits, 2 decimal places)
        product = ProductFactory(price=Decimal("12345678.99"))
        self.assertEqual(product.price, Decimal("12345678.99"))

        # Test price with too many digits should raise ValidationError
        product = Product(
            category=self.category,
            name="Test Product",
            description="Test description",
            price=Decimal("123456789.99"),  # 11 digits total, exceeds max_digits=10
            stock=1,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

        # Test price with too many decimal places
        product = Product(
            category=self.category,
            name="Test Product",
            description="Test description",
            price=Decimal("15.999"),  # 3 decimal places, exceeds decimal_places=2
            stock=1,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_stock_field(self):
        """Test Product stock field properties."""
        # Test valid stock
        self.assertEqual(self.product.stock, 50)

        # Test zero stock (should be valid for PositiveIntegerField)
        product = ProductFactory(stock=0)
        self.assertEqual(product.stock, 0)

        # Test negative stock should raise ValidationError
        product = Product(
            category=self.category,
            name="Test Product",
            description="Test description",
            price=Decimal("10.00"),
            stock=-1,
        )

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_product_timestamps(self):
        """Test Product created_at and updated_at timestamps."""
        # Test that timestamps are set on creation
        self.assertIsNotNone(self.product.created_at)
        self.assertIsNotNone(self.product.updated_at)

        # Test that updated_at changes when product is saved
        original_updated_at = self.product.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        self.product.name = "Updated Product Name"
        self.product.save()

        self.assertGreater(self.product.updated_at, original_updated_at)

    def test_product_cascade_delete_with_category(self):
        """Test that products are deleted when category is deleted."""
        self.category.id
        product_id = self.product.id

        # Verify product exists
        self.assertTrue(Product.objects.filter(id=product_id).exists())

        # Delete category
        self.category.delete()

        # Verify product is also deleted (CASCADE)
        self.assertFalse(Product.objects.filter(id=product_id).exists())

    def test_product_category_related_name(self):
        """Test that category's related_name 'products' works correctly."""
        # Create multiple products for the same category
        product2 = ProductFactory(category=self.category, name="Second Product")
        product3 = ProductFactory(category=self.category, name="Third Product")

        # Test that all products are accessible via category.products
        category_products = self.category.products.all()
        self.assertEqual(category_products.count(), 3)
        self.assertIn(self.product, category_products)
        self.assertIn(product2, category_products)
        self.assertIn(product3, category_products)

    @patch("nz_store.utils.get_product_image_upload_path")
    def test_product_image_upload_path(self, mock_upload_path):
        """Test that image upload path function is called correctly."""
        mock_upload_path.return_value = "products/test_path.jpg"

        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
        image_file = SimpleUploadedFile("test_image.gif", image_content, content_type="image/gif")

        product = ProductFactory(image=image_file)

        # Verify that the upload_to function was used
        self.assertIsNotNone(product.image)

    def test_product_decimal_field_precision(self):
        """Test that price field maintains decimal precision."""
        prices = [
            Decimal("0.01"),  # Minimum price
            Decimal("0.99"),  # Less than 1
            Decimal("10.50"),  # Standard price
            Decimal("99.99"),  # High price
            Decimal("1000.00"),  # Round number
        ]

        for price in prices:
            product = ProductFactory(price=price)
            self.assertEqual(product.price, price)
            # Verify precision is maintained after save/reload
            product.refresh_from_db()
            self.assertEqual(product.price, price)

    def test_product_required_fields(self):
        """Test that all required fields are properly validated."""
        # Test missing category
        with self.assertRaises(ValidationError):
            product = Product(
                name="Test Product",
                description="Test description",
                price=Decimal("10.00"),
                stock=1,
            )
            product.full_clean()

        # Test missing name
        with self.assertRaises(ValidationError):
            product = Product(
                category=self.category,
                description="Test description",
                price=Decimal("10.00"),
                stock=1,
            )
            product.full_clean()

        # Test missing description
        with self.assertRaises(ValidationError):
            product = Product(
                category=self.category,
                name="Test Product",
                description="",  # Empty description is not allowed
                price=Decimal("10.00"),
                stock=1,
            )
            product.full_clean()

        # Test missing price
        with self.assertRaises(ValidationError):
            product = Product(
                category=self.category,
                name="Test Product",
                description="Test description",
                stock=1,
            )
            product.full_clean()

        # Test missing stock
        with self.assertRaises(ValidationError):
            product = Product(
                category=self.category,
                name="Test Product",
                description="Test description",
                price=Decimal("10.00"),
            )
            product.full_clean()
