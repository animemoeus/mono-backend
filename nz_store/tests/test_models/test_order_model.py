import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from nz_store.models import Order
from nz_store.tests.factories import AccountStockFactory, OrderFactory, ProductFactory, TelegramUserFactory


class OrderModelTest(TestCase):
    """Test case for Order model."""

    def setUp(self):
        """Set up test data."""
        self.product = ProductFactory(name="Netflix Premium Account")
        self.account_stock = AccountStockFactory(product=self.product, email="netflix@example.com", is_sold=False)
        self.telegram_user = TelegramUserFactory(telegram_id="123456789", first_name="John", last_name="Doe")
        self.order = OrderFactory(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
            status=Order.ORDER_STATUS_PENDING,
            paid_at=None,
        )

    def test_order_creation(self):
        """Test Order model creation."""
        self.assertIsInstance(self.order, Order)
        self.assertEqual(self.order.product, self.product)
        self.assertEqual(self.order.account_stock, self.account_stock)
        self.assertEqual(self.order.telegram_user, self.telegram_user)
        self.assertEqual(self.order.status, Order.ORDER_STATUS_PENDING)
        self.assertIsNone(self.order.paid_at)
        self.assertIsNotNone(self.order.uuid)
        self.assertIsNotNone(self.order.created_at)
        self.assertIsNotNone(self.order.updated_at)

    def test_order_str_representation(self):
        """Test the string representation of Order."""
        expected_str = f"Order {self.order.uuid} - {self.product.name} ({Order.ORDER_STATUS_PENDING})"
        self.assertEqual(str(self.order), expected_str)

    def test_order_uuid_field(self):
        """Test that UUID field is properly generated and unique."""
        # Check that UUID is valid
        self.assertIsInstance(self.order.uuid, uuid.UUID)

        # Create another order and check UUID uniqueness
        order2 = OrderFactory(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
        )
        self.assertNotEqual(self.order.uuid, order2.uuid)

    def test_order_status_choices(self):
        """Test Order status choices and constants."""
        # Test that status constants are defined correctly
        self.assertEqual(Order.ORDER_STATUS_PENDING, "PENDING")
        self.assertEqual(Order.ORDER_STATUS_COMPLETED, "COMPLETED")
        self.assertEqual(Order.ORDER_STATUS_CANCELLED, "CANCELLED")

        # Test that choices are defined correctly
        expected_choices = [
            ("PENDING", "Pending"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ]
        self.assertEqual(Order.ORDER_STATUS_CHOICES, expected_choices)

        # Test each status value
        for status_value, _ in Order.ORDER_STATUS_CHOICES:
            order = OrderFactory(status=status_value)
            self.assertEqual(order.status, status_value)

    def test_order_status_default_value(self):
        """Test that default status is PENDING."""
        order = Order.objects.create(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
        )
        self.assertEqual(order.status, Order.ORDER_STATUS_PENDING)

    def test_order_status_field_validation(self):
        """Test Order status field validation."""
        # Test invalid status
        order = Order(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
            status="INVALID_STATUS",
        )

        with self.assertRaises(ValidationError):
            order.full_clean()

    def test_order_product_foreign_key(self):
        """Test Order product foreign key relationship."""
        self.assertEqual(self.order.product.id, self.product.id)
        self.assertEqual(self.order.product.name, "Netflix Premium Account")

        # Test that order appears in product's related orders
        self.assertIn(self.order, self.product.orders.all())

    def test_order_account_stock_foreign_key(self):
        """Test Order account_stock foreign key relationship."""
        self.assertEqual(self.order.account_stock.id, self.account_stock.id)
        self.assertEqual(self.order.account_stock.email, "netflix@example.com")

        # Test that order appears in account_stock's related orders
        self.assertIn(self.order, self.account_stock.orders.all())

    def test_order_telegram_user_foreign_key(self):
        """Test Order telegram_user foreign key relationship."""
        self.assertEqual(self.order.telegram_user.id, self.telegram_user.id)
        self.assertEqual(self.order.telegram_user.telegram_id, "123456789")

        # Test that order appears in telegram_user's related orders
        self.assertIn(self.order, self.telegram_user.orders.all())

    def test_order_paid_at_field(self):
        """Test Order paid_at field properties."""
        # Test None paid_at (null=True, blank=True)
        self.assertIsNone(self.order.paid_at)

        # Test setting paid_at
        now = timezone.now()
        self.order.paid_at = now
        self.order.save()
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid_at, now)

        # Test creating order with paid_at
        paid_order = OrderFactory(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
            status=Order.ORDER_STATUS_COMPLETED,
            paid_at=now,
        )
        self.assertEqual(paid_order.paid_at, now)

    def test_order_timestamps(self):
        """Test Order created_at and updated_at timestamps."""
        # Test that timestamps are set on creation
        self.assertIsNotNone(self.order.created_at)
        self.assertIsNotNone(self.order.updated_at)

        # Test that updated_at changes when order is saved
        original_updated_at = self.order.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        self.order.status = Order.ORDER_STATUS_COMPLETED
        self.order.save()

        self.assertGreater(self.order.updated_at, original_updated_at)

    def test_order_cascade_delete_with_product(self):
        """Test that orders are deleted when product is deleted."""
        order_id = self.order.id

        # Verify order exists
        self.assertTrue(Order.objects.filter(id=order_id).exists())

        # Delete product
        self.product.delete()

        # Verify order is also deleted (CASCADE)
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_order_cascade_delete_with_account_stock(self):
        """Test that orders are deleted when account_stock is deleted."""
        order_id = self.order.id

        # Verify order exists
        self.assertTrue(Order.objects.filter(id=order_id).exists())

        # Delete account_stock
        self.account_stock.delete()

        # Verify order is also deleted (CASCADE)
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_order_cascade_delete_with_telegram_user(self):
        """Test that orders are deleted when telegram_user is deleted."""
        order_id = self.order.id

        # Verify order exists
        self.assertTrue(Order.objects.filter(id=order_id).exists())

        # Delete telegram_user
        self.telegram_user.delete()

        # Verify order is also deleted (CASCADE)
        self.assertFalse(Order.objects.filter(id=order_id).exists())

    def test_order_related_names(self):
        """Test that all related_names work correctly."""
        # Create multiple orders for testing
        order2 = OrderFactory(
            product=self.product,
            account_stock=self.account_stock,
            telegram_user=self.telegram_user,
        )

        # Test product.orders
        product_orders = self.product.orders.all()
        self.assertEqual(product_orders.count(), 2)
        self.assertIn(self.order, product_orders)
        self.assertIn(order2, product_orders)

        # Test account_stock.orders
        account_stock_orders = self.account_stock.orders.all()
        self.assertEqual(account_stock_orders.count(), 2)
        self.assertIn(self.order, account_stock_orders)
        self.assertIn(order2, account_stock_orders)

        # Test telegram_user.orders
        telegram_user_orders = self.telegram_user.orders.all()
        self.assertEqual(telegram_user_orders.count(), 2)
        self.assertIn(self.order, telegram_user_orders)
        self.assertIn(order2, telegram_user_orders)

    def test_order_required_fields(self):
        """Test that all required fields are properly validated."""
        # Test missing product
        with self.assertRaises(ValidationError):
            order = Order(
                account_stock=self.account_stock,
                telegram_user=self.telegram_user,
                status=Order.ORDER_STATUS_PENDING,
            )
            order.full_clean()

        # Test missing account_stock
        with self.assertRaises(ValidationError):
            order = Order(
                product=self.product,
                telegram_user=self.telegram_user,
                status=Order.ORDER_STATUS_PENDING,
            )
            order.full_clean()

        # Test missing telegram_user
        with self.assertRaises(ValidationError):
            order = Order(
                product=self.product,
                account_stock=self.account_stock,
                status=Order.ORDER_STATUS_PENDING,
            )
            order.full_clean()

    def test_order_status_transitions(self):
        """Test common order status transitions."""
        # Test PENDING -> COMPLETED
        self.assertEqual(self.order.status, Order.ORDER_STATUS_PENDING)
        self.assertIsNone(self.order.paid_at)

        self.order.status = Order.ORDER_STATUS_COMPLETED
        self.order.paid_at = timezone.now()
        self.order.save()

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(self.order.paid_at)

        # Test PENDING -> CANCELLED
        cancelled_order = OrderFactory(status=Order.ORDER_STATUS_PENDING)
        cancelled_order.status = Order.ORDER_STATUS_CANCELLED
        cancelled_order.save()

        cancelled_order.refresh_from_db()
        self.assertEqual(cancelled_order.status, Order.ORDER_STATUS_CANCELLED)
        self.assertIsNone(cancelled_order.paid_at)  # Should remain None for cancelled orders

    def test_order_filtering_by_status(self):
        """Test filtering orders by status."""
        # Create orders with different statuses
        pending_order = OrderFactory(status=Order.ORDER_STATUS_PENDING)
        completed_order = OrderFactory(status=Order.ORDER_STATUS_COMPLETED, paid_at=timezone.now())
        cancelled_order = OrderFactory(status=Order.ORDER_STATUS_CANCELLED)

        # Test filtering by each status
        pending_orders = Order.objects.filter(status=Order.ORDER_STATUS_PENDING)
        self.assertIn(self.order, pending_orders)  # from setUp
        self.assertIn(pending_order, pending_orders)
        self.assertEqual(pending_orders.count(), 2)

        completed_orders = Order.objects.filter(status=Order.ORDER_STATUS_COMPLETED)
        self.assertIn(completed_order, completed_orders)
        self.assertEqual(completed_orders.count(), 1)

        cancelled_orders = Order.objects.filter(status=Order.ORDER_STATUS_CANCELLED)
        self.assertIn(cancelled_order, cancelled_orders)
        self.assertEqual(cancelled_orders.count(), 1)

    def test_order_filtering_by_paid_status(self):
        """Test filtering orders by paid status."""
        # Create paid and unpaid orders
        paid_order = OrderFactory(status=Order.ORDER_STATUS_COMPLETED, paid_at=timezone.now())
        unpaid_order = OrderFactory(status=Order.ORDER_STATUS_PENDING, paid_at=None)

        # Test filtering paid orders
        paid_orders = Order.objects.exclude(paid_at__isnull=True)
        self.assertIn(paid_order, paid_orders)
        self.assertEqual(paid_orders.count(), 1)

        # Test filtering unpaid orders (including self.order from setUp)
        unpaid_orders = Order.objects.filter(paid_at__isnull=True)
        self.assertIn(self.order, unpaid_orders)
        self.assertIn(unpaid_order, unpaid_orders)
        self.assertEqual(unpaid_orders.count(), 2)

    def test_order_string_representation_with_different_statuses(self):
        """Test string representation with different order statuses."""
        # Test with each status
        statuses = [
            Order.ORDER_STATUS_PENDING,
            Order.ORDER_STATUS_COMPLETED,
            Order.ORDER_STATUS_CANCELLED,
        ]

        for status in statuses:
            order = OrderFactory(product=self.product, status=status)
            expected_str = f"Order {order.uuid} - {self.product.name} ({status})"
            self.assertEqual(str(order), expected_str)

    def test_order_business_logic(self):
        """Test business logic scenarios."""
        # Test that account_stock and product should match
        different_product = ProductFactory(name="Spotify Premium")
        different_account_stock = AccountStockFactory(product=different_product)

        # This should be allowed at model level but might be validated at business logic level
        order = Order.objects.create(
            product=self.product,  # Netflix product
            account_stock=different_account_stock,  # Spotify account stock
            telegram_user=self.telegram_user,
            status=Order.ORDER_STATUS_PENDING,
        )

        # The order is created successfully, but this might be a business rule violation
        # that should be handled at the application level
        self.assertNotEqual(order.product, order.account_stock.product)
