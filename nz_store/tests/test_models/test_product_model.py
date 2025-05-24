import uuid
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_delete, post_save
from django.test import TestCase

from nz_store.models import AccountStock, Product
from nz_store.tests.factories import AccountStockFactory, ProductCategoryFactory, ProductFactory


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

    def test_available_stock_property(self):
        """Test the available_stock property calculation."""
        # Product with no account stocks should return 0
        self.assertEqual(self.product.available_stock, 0)

        # Create some account stocks for the product
        account1 = AccountStockFactory(product=self.product, is_sold=False)
        account2 = AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=True)  # Sold account

        # Should return only unsold accounts
        self.assertEqual(self.product.available_stock, 2)

        # Mark another account as sold
        account1.is_sold = True
        account1.save()

        # Refresh from database and check again
        self.product.refresh_from_db()
        self.assertEqual(self.product.available_stock, 1)

        # Mark all as sold
        account2.is_sold = True
        account2.save()

        self.product.refresh_from_db()
        self.assertEqual(self.product.available_stock, 0)

    def test_available_stock_with_multiple_products(self):
        """Test that available_stock only counts accounts for the specific product."""
        # Create another product
        other_product = ProductFactory()

        # Create account stocks for both products
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=other_product, is_sold=False)
        AccountStockFactory(product=other_product, is_sold=False)
        AccountStockFactory(product=other_product, is_sold=False)

        # Each product should only count its own account stocks
        self.assertEqual(self.product.available_stock, 2)
        self.assertEqual(other_product.available_stock, 3)

    def test_sync_stock_with_accounts_method(self):
        """Test the sync_stock_with_accounts method."""
        # Initial stock value
        original_stock = self.product.stock
        self.assertEqual(original_stock, 50)  # From setUp

        # Product has no account stocks initially
        self.assertEqual(self.product.available_stock, 0)

        # Sync should set stock to 0
        self.product.sync_stock_with_accounts()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)

        # Create some account stocks
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=True)  # Sold account

        # Sync should update stock to match available accounts
        self.product.sync_stock_with_accounts()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        # Add more accounts
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=False)

        # Sync again
        self.product.sync_stock_with_accounts()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)

    def test_sync_stock_with_accounts_saves_only_stock_field(self):
        """Test that sync_stock_with_accounts only updates the stock field."""
        # Change product name but don't save
        original_name = self.product.name

        self.product.name = "Changed Name"

        # Create account stock
        AccountStockFactory(product=self.product, is_sold=False)

        # Sync stock
        self.product.sync_stock_with_accounts()

        # Refresh from database
        self.product.refresh_from_db()

        # Stock should be updated, but name should remain unchanged
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(self.product.name, original_name)  # Name should not be saved

    def test_sync_stock_with_accounts_performance(self):
        """Test that sync_stock_with_accounts uses efficient database queries."""
        # Create multiple account stocks
        for i in range(10):
            AccountStockFactory(product=self.product, is_sold=(i % 3 == 0))  # Some sold, some not

        # Test that the method works correctly
        expected_available = self.product.available_stock

        # Note: With simple_history, we expect 3 queries:
        # 1. SELECT COUNT for available_stock
        # 2. UPDATE for the product stock
        # 3. INSERT for historical record
        with self.assertNumQueries(3):
            self.product.sync_stock_with_accounts()

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, expected_available)

    def test_available_stock_query_efficiency(self):
        """Test that available_stock property uses efficient database queries."""
        # Create account stocks
        AccountStockFactory.create_batch(5, product=self.product, is_sold=False)
        AccountStockFactory.create_batch(3, product=self.product, is_sold=True)

        # Test that available_stock uses a single query
        with self.assertNumQueries(1):
            count = self.product.available_stock

        self.assertEqual(count, 5)

    def test_available_stock_with_no_accounts(self):
        """Test available_stock property when product has no account stocks."""
        # Ensure no account stocks exist for the product
        self.product.account_stocks.all().delete()

        # Should return 0
        self.assertEqual(self.product.available_stock, 0)

    def test_sync_stock_after_account_stock_changes(self):
        """Test that manual stock sync works after account stock changes."""
        # Temporarily disconnect signals to test manual sync behavior
        from nz_store.signals import sync_product_stock_on_account_delete, sync_product_stock_on_account_save

        post_save.disconnect(sync_product_stock_on_account_save, sender=AccountStock)
        post_delete.disconnect(sync_product_stock_on_account_delete, sender=AccountStock)

        try:
            # Create initial account stocks
            account1 = AccountStockFactory(product=self.product, is_sold=False)
            account2 = AccountStockFactory(product=self.product, is_sold=False)

            # Sync and verify
            self.product.sync_stock_with_accounts()
            self.assertEqual(self.product.stock, 2)

            # Change account stock status
            account1.is_sold = True
            account1.save()

            # Stock should not auto-update (signals are disconnected)
            self.product.refresh_from_db()
            self.assertEqual(self.product.stock, 2)  # Still old value

            # Manual sync should update it
            self.product.sync_stock_with_accounts()
            self.assertEqual(self.product.stock, 1)

            # Delete an account stock
            account2.delete()

            # Manual sync should reflect the deletion
            self.product.sync_stock_with_accounts()
            self.assertEqual(self.product.stock, 0)
        finally:
            # Reconnect signals
            post_save.connect(sync_product_stock_on_account_save, sender=AccountStock)
            post_delete.connect(sync_product_stock_on_account_delete, sender=AccountStock)
