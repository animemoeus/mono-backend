import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from nz_store.models import TelegramUser
from nz_store.tests.factories import TelegramUserFactory


class TelegramUserModelTest(TestCase):
    """Test case for TelegramUser model."""

    def setUp(self):
        """Set up test data."""
        self.telegram_user = TelegramUserFactory(
            telegram_id="123456789",
            username="testuser",
            first_name="John",
            last_name="Doe",
        )

    def test_telegram_user_creation(self):
        """Test TelegramUser model creation."""
        self.assertIsInstance(self.telegram_user, TelegramUser)
        self.assertEqual(self.telegram_user.telegram_id, "123456789")
        self.assertEqual(self.telegram_user.username, "testuser")
        self.assertEqual(self.telegram_user.first_name, "John")
        self.assertEqual(self.telegram_user.last_name, "Doe")
        self.assertIsNotNone(self.telegram_user.uuid)
        self.assertIsNotNone(self.telegram_user.created_at)
        self.assertIsNotNone(self.telegram_user.updated_at)

    def test_telegram_user_str_representation(self):
        """Test the string representation of TelegramUser."""
        expected_str = "John Doe"
        self.assertEqual(str(self.telegram_user), expected_str)

    def test_telegram_user_str_representation_with_none_last_name(self):
        """Test string representation when last_name is None."""
        user = TelegramUserFactory(first_name="Jane", last_name=None)
        expected_str = "Jane None"
        self.assertEqual(str(user), expected_str)

    def test_telegram_user_str_representation_with_none_names(self):
        """Test string representation when both names are None."""
        user = TelegramUserFactory(first_name=None, last_name=None)
        expected_str = "None None"
        self.assertEqual(str(user), expected_str)

    def test_telegram_user_uuid_field(self):
        """Test that UUID field is properly generated and unique."""
        # Check that UUID is valid
        self.assertIsInstance(self.telegram_user.uuid, uuid.UUID)

        # Create another user and check UUID uniqueness
        user2 = TelegramUserFactory(telegram_id="987654321")
        self.assertNotEqual(self.telegram_user.uuid, user2.uuid)

    def test_telegram_user_telegram_id_field(self):
        """Test TelegramUser telegram_id field properties."""
        # Test valid telegram_id
        self.assertEqual(self.telegram_user.telegram_id, "123456789")

        # Test max length
        long_telegram_id = "1" * 256  # Exceeds max_length of 255
        user = TelegramUser(
            telegram_id=long_telegram_id,
            username="test",
            first_name="Test",
            last_name="User",
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_user_telegram_id_uniqueness(self):
        """Test that telegram_id must be unique."""
        # Try to create another user with the same telegram_id
        with self.assertRaises(IntegrityError):
            TelegramUser.objects.create(
                telegram_id="123456789",  # Same as self.telegram_user
                username="anotheruser",
                first_name="Jane",
                last_name="Smith",
            )

    def test_telegram_user_username_field(self):
        """Test TelegramUser username field properties."""
        # Test valid username
        self.assertEqual(self.telegram_user.username, "testuser")

        # Test None username (blank=True, null=True)
        user = TelegramUserFactory(username=None)
        self.assertIsNone(user.username)

        # Test empty string username
        user = TelegramUserFactory(username="")
        self.assertEqual(user.username, "")

        # Test max length
        long_username = "u" * 256  # Exceeds max_length of 255
        user = TelegramUser(
            telegram_id="999888777",
            username=long_username,
            first_name="Test",
            last_name="User",
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_user_first_name_field(self):
        """Test TelegramUser first_name field properties."""
        # Test valid first_name
        self.assertEqual(self.telegram_user.first_name, "John")

        # Test None first_name (blank=True, null=True)
        user = TelegramUserFactory(first_name=None)
        self.assertIsNone(user.first_name)

        # Test empty string first_name
        user = TelegramUserFactory(first_name="")
        self.assertEqual(user.first_name, "")

        # Test max length
        long_first_name = "J" * 256  # Exceeds max_length of 255
        user = TelegramUser(
            telegram_id="888777666",
            username="test",
            first_name=long_first_name,
            last_name="User",
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_user_last_name_field(self):
        """Test TelegramUser last_name field properties."""
        # Test valid last_name
        self.assertEqual(self.telegram_user.last_name, "Doe")

        # Test None last_name (blank=True, null=True)
        user = TelegramUserFactory(last_name=None)
        self.assertIsNone(user.last_name)

        # Test empty string last_name
        user = TelegramUserFactory(last_name="")
        self.assertEqual(user.last_name, "")

        # Test max length
        long_last_name = "D" * 256  # Exceeds max_length of 255
        user = TelegramUser(
            telegram_id="777666555",
            username="test",
            first_name="Test",
            last_name=long_last_name,
        )

        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_telegram_user_timestamps(self):
        """Test TelegramUser created_at and updated_at timestamps."""
        # Test that timestamps are set on creation
        self.assertIsNotNone(self.telegram_user.created_at)
        self.assertIsNotNone(self.telegram_user.updated_at)

        # Test that updated_at changes when user is saved
        original_updated_at = self.telegram_user.updated_at

        # Small delay to ensure timestamp difference
        import time

        time.sleep(0.01)

        self.telegram_user.username = "updateduser"
        self.telegram_user.save()

        self.assertGreater(self.telegram_user.updated_at, original_updated_at)

    def test_telegram_user_required_fields(self):
        """Test that required fields are properly validated."""
        # Test missing telegram_id (should raise ValidationError)
        with self.assertRaises(ValidationError):
            user = TelegramUser(username="test", first_name="Test", last_name="User")
            user.full_clean()

    def test_telegram_user_optional_fields(self):
        """Test that optional fields can be None or empty."""
        # Create user with only required field
        user = TelegramUser.objects.create(telegram_id="555444333")

        self.assertEqual(user.telegram_id, "555444333")
        self.assertIsNone(user.username)
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)

    def test_telegram_user_get_or_create_behavior(self):
        """Test get_or_create behavior with telegram_id."""
        # Test creating a new user
        user1, created1 = TelegramUser.objects.get_or_create(
            telegram_id="111222333",
            defaults={"username": "newuser", "first_name": "New", "last_name": "User"},
        )
        self.assertTrue(created1)
        self.assertEqual(user1.telegram_id, "111222333")
        self.assertEqual(user1.username, "newuser")

        # Test getting existing user
        user2, created2 = TelegramUser.objects.get_or_create(
            telegram_id="111222333",
            defaults={
                "username": "differentuser",  # This should be ignored
                "first_name": "Different",
                "last_name": "Person",
            },
        )
        self.assertFalse(created2)
        self.assertEqual(user2.id, user1.id)
        self.assertEqual(user2.username, "newuser")  # Original username preserved

    def test_telegram_user_filtering_and_queries(self):
        """Test various filtering and query operations."""
        # Create additional users for testing
        user1 = TelegramUserFactory(username="alice", first_name="Alice")
        user2 = TelegramUserFactory(username="bob", first_name="Bob")
        user3 = TelegramUserFactory(username=None, first_name="Charlie")

        # Test filtering by username
        users_with_username = TelegramUser.objects.exclude(username__isnull=True)
        self.assertIn(self.telegram_user, users_with_username)
        self.assertIn(user1, users_with_username)
        self.assertIn(user2, users_with_username)
        self.assertNotIn(user3, users_with_username)

        # Test filtering by first_name
        alice_users = TelegramUser.objects.filter(first_name="Alice")
        self.assertEqual(alice_users.count(), 1)
        self.assertIn(user1, alice_users)

        # Test ordering
        ordered_users = TelegramUser.objects.order_by("created_at")
        self.assertEqual(ordered_users.first(), self.telegram_user)  # Created first in setUp

    def test_telegram_user_update_operations(self):
        """Test update operations on TelegramUser."""
        original_username = self.telegram_user.username
        original_updated_at = self.telegram_user.updated_at

        # Update username
        self.telegram_user.username = "updated_username"
        self.telegram_user.save()

        # Verify changes
        self.telegram_user.refresh_from_db()
        self.assertEqual(self.telegram_user.username, "updated_username")
        self.assertNotEqual(self.telegram_user.username, original_username)
        self.assertGreater(self.telegram_user.updated_at, original_updated_at)

    def test_telegram_user_bulk_operations(self):
        """Test bulk operations with TelegramUser."""
        # Create multiple users
        users_data = [
            {"telegram_id": "100", "username": "user1", "first_name": "User1"},
            {"telegram_id": "200", "username": "user2", "first_name": "User2"},
            {"telegram_id": "300", "username": "user3", "first_name": "User3"},
        ]

        users = [TelegramUser(**data) for data in users_data]
        created_users = TelegramUser.objects.bulk_create(users)

        self.assertEqual(len(created_users), 3)
        self.assertEqual(
            TelegramUser.objects.filter(telegram_id__in=["100", "200", "300"]).count(),
            3,
        )
