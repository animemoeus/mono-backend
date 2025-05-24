from django.test import TestCase

from nz_store.models import AccountStock
from nz_store.tests.factories import AccountStockFactory, ProductFactory


class SignalTest(TestCase):
    """Test case for nz_store signals."""

    def setUp(self):
        """Set up test data."""
        self.product = ProductFactory(stock=10)

    def test_product_stock_syncs_on_account_stock_creation(self):
        """Test that product stock syncs when AccountStock is created."""
        # Initially product stock should remain unchanged
        self.assertEqual(self.product.stock, 10)

        # Create an account stock
        AccountStockFactory(product=self.product, is_sold=False)

        # Product stock should now be synced to 1
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

        # Create another account stock
        AccountStockFactory(product=self.product, is_sold=False)

        # Product stock should now be 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_product_stock_syncs_on_account_stock_update(self):
        """Test that product stock syncs when AccountStock is updated."""
        # Create account stocks
        account1 = AccountStockFactory(product=self.product, is_sold=False)
        account2 = AccountStockFactory(product=self.product, is_sold=False)

        # Product stock should be 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        # Mark one as sold
        account1.is_sold = True
        account1.save()

        # Product stock should now be 1
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

        # Mark the other as sold
        account2.is_sold = True
        account2.save()

        # Product stock should now be 0
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)

    def test_product_stock_syncs_on_account_stock_deletion(self):
        """Test that product stock syncs when AccountStock is deleted."""
        # Create account stocks
        account1 = AccountStockFactory(product=self.product, is_sold=False)
        account2 = AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=self.product, is_sold=True)  # Sold account

        # Product stock should be 2 (only unsold accounts)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        # Delete one unsold account
        account1.delete()

        # Product stock should now be 1
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 1)

        # Delete the other unsold account
        account2.delete()

        # Product stock should now be 0
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)

    def test_signal_only_affects_related_product(self):
        """Test that signals only affect the related product."""
        # Create another product
        other_product = ProductFactory(stock=5)

        # Create account stocks for both products
        AccountStockFactory(product=self.product, is_sold=False)
        AccountStockFactory(product=other_product, is_sold=False)

        # Each product should have its own stock count
        self.product.refresh_from_db()
        other_product.refresh_from_db()

        self.assertEqual(self.product.stock, 1)
        self.assertEqual(other_product.stock, 1)

        # Update account stock for one product
        AccountStockFactory(product=self.product, is_sold=False)

        # Only the related product should be affected
        self.product.refresh_from_db()
        other_product.refresh_from_db()

        self.assertEqual(self.product.stock, 2)
        self.assertEqual(other_product.stock, 1)  # Should remain unchanged

    def test_signal_with_sold_account_changes(self):
        """Test signals work correctly when changing is_sold status."""
        # Create account stocks - some sold, some not
        account1 = AccountStockFactory(product=self.product, is_sold=False)
        account2 = AccountStockFactory(product=self.product, is_sold=True)
        AccountStockFactory(product=self.product, is_sold=False)

        # Product stock should be 2 (unsold accounts)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        # Change sold account to unsold
        account2.is_sold = False
        account2.save()

        # Product stock should now be 3
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # Change unsold account to sold
        account1.is_sold = True
        account1.save()

        # Product stock should now be 2
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_bulk_account_stock_operations(self):
        """Test signals work with bulk operations."""
        # Create multiple account stocks
        accounts = AccountStockFactory.create_batch(5, product=self.product, is_sold=False)

        # Product stock should be 5
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

        # Bulk update some to sold
        AccountStock.objects.filter(id__in=[accounts[0].id, accounts[1].id]).update(is_sold=True)

        # Note: bulk_update doesn't trigger signals, so we need to manually sync
        # This test documents the current behavior
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)  # Still 5 because signals didn't fire

        # Manual sync should fix it
        self.product.sync_stock_with_accounts()
        self.assertEqual(self.product.stock, 3)

    def test_signal_performance_with_multiple_saves(self):
        """Test that signals don't cause performance issues with multiple saves."""
        # Create initial account stock
        account = AccountStockFactory(product=self.product, is_sold=False)

        # Multiple saves should each trigger the signal
        for i in range(3):
            account.description = f"Updated description {i}"
            account.save()

            # Product stock should remain consistent
            self.product.refresh_from_db()
            self.assertEqual(self.product.stock, 1)

        # Change is_sold status
        account.is_sold = True
        account.save()

        # Product stock should update
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
