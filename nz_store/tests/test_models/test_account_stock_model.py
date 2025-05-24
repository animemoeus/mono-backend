import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase

from nz_store.models import AccountStock
from nz_store.tests.factories import AccountStockFactory, ProductFactory


class AccountStockModelTest(TestCase):
    """Test case for AccountStock model."""

    def setUp(self):
        """Set up test data."""
        self.product = ProductFactory(
            name="Netflix Premium Account",
            description="High-quality Netflix premium account",
        )
        self.account_stock = AccountStockFactory(
            product=self.product,
            email="test@example.com",
            username="testuser123",
            password="securepassword",
            description="Premium account with 4K streaming",
            is_sold=False,
        )

    def test_account_stock_creation(self):
        """Test AccountStock model creation."""
        self.assertIsInstance(self.account_stock, AccountStock)
        self.assertEqual(self.account_stock.email, "test@example.com")
        self.assertEqual(self.account_stock.username, "testuser123")
        self.assertEqual(self.account_stock.password, "securepassword")
        self.assertEqual(self.account_stock.description, "Premium account with 4K streaming")
        self.assertFalse(self.account_stock.is_sold)
        self.assertEqual(self.account_stock.product, self.product)
        self.assertIsNotNone(self.account_stock.uuid)
        self.assertIsNotNone(self.account_stock.created_at)
        self.assertIsNotNone(self.account_stock.updated_at)

    def test_account_stock_str_representation(self):
        """Test the string representation of AccountStock."""
        expected_str = f"{self.product.name} - {self.account_stock.email}  {self.account_stock.username}"
        self.assertEqual(str(self.account_stock), expected_str)

    def test_account_stock_uuid_field(self):
        """Test that UUID field is properly generated and unique."""
        # Check that UUID is valid
        self.assertIsInstance(self.account_stock.uuid, uuid.UUID)

        # Create another account stock and check UUID uniqueness
        account_stock2 = AccountStockFactory(product=self.product)
        self.assertNotEqual(self.account_stock.uuid, account_stock2.uuid)

    def test_account_stock_product_foreign_key(self):
        """Test AccountStock product foreign key relationship."""
        self.assertEqual(self.account_stock.product.id, self.product.id)
        self.assertEqual(self.account_stock.product.name, "Netflix Premium Account")

        # Test that account stock appears in product's related account stocks
        self.assertIn(self.account_stock, self.product.account_stocks.all())

    def test_account_stock_email_field(self):
        """Test AccountStock email field properties."""
        # Test valid email
        self.assertEqual(self.account_stock.email, "test@example.com")

        # Test empty email (default="")
        account_stock = AccountStockFactory(email="")
        self.assertEqual(account_stock.email, "")

        # Test max length
        long_email = "a" * 248 + "@test.com"  # Total 256 chars, exceeds max_length of 255
        account_stock = AccountStock(
            product=self.product,
            email=long_email,
            username="test",
            password="test",
            description="test",
        )

        with self.assertRaises(ValidationError):
            account_stock.full_clean()

        # Test invalid email format
        account_stock = AccountStock(
            product=self.product,
            email="invalid-email",
            username="test",
            password="test",
            description="test",
        )

        with self.assertRaises(ValidationError):
            account_stock.full_clean()

    def test_account_stock_username_field(self):
        """Test AccountStock username field properties."""
        # Test valid username
        self.assertEqual(self.account_stock.username, "testuser123")

        # Test empty username (default="")
        account_stock = AccountStockFactory(username="")
        self.assertEqual(account_stock.username, "")

        # Test max length
        long_username = "a" * 256  # Exceeds max_length of 255
        account_stock = AccountStock(
            product=self.product,
            email="test@example.com",
            username=long_username,
            password="test",
            description="test",
        )

        with self.assertRaises(ValidationError):
            account_stock.full_clean()

    def test_account_stock_password_field(self):
        """Test AccountStock password field properties."""
        # Test valid password
        self.assertEqual(self.account_stock.password, "securepassword")

        # Test empty password (default="")
        account_stock = AccountStockFactory(password="")
        self.assertEqual(account_stock.password, "")

        # Test max length
        long_password = "a" * 256  # Exceeds max_length of 255
        account_stock = AccountStock(
            product=self.product,
            email="test@example.com",
            username="test",
            password=long_password,
            description="test",
        )

        with self.assertRaises(ValidationError):
            account_stock.full_clean()

    def test_account_stock_description_field(self):
        """Test AccountStock description field properties."""
        # Test valid description
        self.assertEqual(self.account_stock.description, "Premium account with 4K streaming")

        # Test empty description (default="")
        account_stock = AccountStockFactory(description="")
        self.assertEqual(account_stock.description, "")

        # Test long description (TextField should accept long text)
        long_description = "a" * 1000
        account_stock = AccountStockFactory(description=long_description)
        self.assertEqual(account_stock.description, long_description)

    def test_account_stock_is_sold_field(self):
        """Test AccountStock is_sold field properties."""
        # Test default value
        self.assertFalse(self.account_stock.is_sold)

        # Test setting to True
        self.account_stock.is_sold = True
        self.account_stock.save()
        self.account_stock.refresh_from_db()
        self.assertTrue(self.account_stock.is_sold)

        # Test creating with is_sold=True
        sold_account = AccountStockFactory(is_sold=True)
        self.assertTrue(sold_account.is_sold)

    def test_account_stock_default_values(self):
        """Test AccountStock default field values."""
        # Create minimal account stock to test defaults
        account_stock = AccountStock.objects.create(product=self.product)

        self.assertEqual(account_stock.email, "")
        self.assertEqual(account_stock.username, "")
        self.assertEqual(account_stock.password, "")
        self.assertEqual(account_stock.description, "")
        self.assertFalse(account_stock.is_sold)

    def test_account_stock_timestamps(self):
        """Test AccountStock created_at and updated_at timestamps."""
        # Test that timestamps are set on creation
        self.assertIsNotNone(self.account_stock.created_at)
        self.assertIsNotNone(self.account_stock.updated_at)

        # Test that updated_at changes when account stock is saved
        original_updated_at = self.account_stock.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        self.account_stock.is_sold = True
        self.account_stock.save()

        self.assertGreater(self.account_stock.updated_at, original_updated_at)

    def test_account_stock_cascade_delete_with_product(self):
        """Test that account stocks are deleted when product is deleted."""
        self.product.id
        account_stock_id = self.account_stock.id

        # Verify account stock exists
        self.assertTrue(AccountStock.objects.filter(id=account_stock_id).exists())

        # Delete product
        self.product.delete()

        # Verify account stock is also deleted (CASCADE)
        self.assertFalse(AccountStock.objects.filter(id=account_stock_id).exists())

    def test_account_stock_product_related_name(self):
        """Test that product's related_name 'account_stocks' works correctly."""
        # Create multiple account stocks for the same product
        account_stock2 = AccountStockFactory(product=self.product, email="test2@example.com")
        account_stock3 = AccountStockFactory(product=self.product, email="test3@example.com")

        # Test that all account stocks are accessible via product.account_stocks
        product_account_stocks = self.product.account_stocks.all()
        self.assertEqual(product_account_stocks.count(), 3)
        self.assertIn(self.account_stock, product_account_stocks)
        self.assertIn(account_stock2, product_account_stocks)
        self.assertIn(account_stock3, product_account_stocks)

    def test_account_stock_required_fields(self):
        """Test that required fields are properly validated."""
        # Test missing product (should raise ValidationError)
        with self.assertRaises(ValidationError):
            account_stock = AccountStock(
                email="test@example.com",
                username="test",
                password="test",
                description="test",
            )
            account_stock.full_clean()

    def test_account_stock_filtering_by_sold_status(self):
        """Test filtering account stocks by sold status."""
        # Create sold and unsold account stocks
        sold_account1 = AccountStockFactory(product=self.product, is_sold=True)
        sold_account2 = AccountStockFactory(product=self.product, is_sold=True)
        unsold_account1 = AccountStockFactory(product=self.product, is_sold=False)
        unsold_account2 = AccountStockFactory(product=self.product, is_sold=False)

        # Test filtering sold accounts
        sold_accounts = AccountStock.objects.filter(is_sold=True)
        self.assertEqual(sold_accounts.count(), 2)
        self.assertIn(sold_account1, sold_accounts)
        self.assertIn(sold_account2, sold_accounts)

        # Test filtering unsold accounts (including the one from setUp)
        unsold_accounts = AccountStock.objects.filter(is_sold=False)
        self.assertEqual(unsold_accounts.count(), 3)  # Including self.account_stock
        self.assertIn(self.account_stock, unsold_accounts)
        self.assertIn(unsold_account1, unsold_accounts)
        self.assertIn(unsold_account2, unsold_accounts)

    def test_account_stock_string_representation_with_empty_fields(self):
        """Test string representation with empty email and username."""
        account_stock = AccountStockFactory(product=self.product, email="", username="")
        expected_str = f"{self.product.name} -   "  # Empty email and username with spaces
        self.assertEqual(str(account_stock), expected_str)
