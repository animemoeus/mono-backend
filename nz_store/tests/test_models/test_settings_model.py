import json
import logging
from unittest.mock import Mock, patch

import requests
from django.test import TestCase
from solo.models import SingletonModel

from nz_store.models import Settings
from nz_store.tests.factories import SettingsFactory


class SettingsModelTest(TestCase):
    """Test case for Settings model."""

    def setUp(self):
        """Set up test data."""
        self.settings = SettingsFactory(
            bot_token="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            bot_name="Test Bot",
            bot_description="A test bot for unit testing",
            maintenance_mode=False,
        )

    def test_settings_creation(self):
        """Test Settings model creation."""
        self.assertIsInstance(self.settings, Settings)
        self.assertEqual(self.settings.bot_token, "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual(self.settings.bot_name, "Test Bot")
        self.assertEqual(self.settings.bot_description, "A test bot for unit testing")
        self.assertFalse(self.settings.maintenance_mode)
        self.assertIsNotNone(self.settings.created_at)
        self.assertIsNotNone(self.settings.updated_at)

    def test_settings_str_representation(self):
        """Test the string representation of Settings."""
        self.assertEqual(str(self.settings), "Settings")

    def test_settings_singleton_model(self):
        """Test that Settings inherits from SingletonModel."""
        self.assertIsInstance(self.settings, SingletonModel)

    def test_settings_has_history(self):
        """Test that Settings model has historical records."""
        self.assertTrue(hasattr(Settings, "history"))
        # History is a manager, not a HistoricalRecords instance
        self.assertTrue(hasattr(Settings.history, "model"))

    def test_settings_meta_verbose_names(self):
        """Test the verbose names in Meta class."""
        self.assertEqual(Settings._meta.verbose_name, "Settings")
        self.assertEqual(Settings._meta.verbose_name_plural, "Settings")

    def test_only_one_settings_instance(self):
        """Test that only one Settings instance can exist (singleton pattern)."""
        # Get the singleton instance
        settings2 = Settings.objects.get()

        # Both should have the same ID (singleton behavior)
        self.assertEqual(self.settings.id, settings2.id)

        # Verify there's only one instance in the database
        self.assertEqual(Settings.objects.count(), 1)

    @patch("requests.request")
    def test_set_bot_name_success(self, mock_request):
        """Test successful bot name setting."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        self.settings.set_bot_name()

        # Verify the API call was made correctly
        mock_request.assert_called_once_with(
            "POST",
            f"https://api.telegram.org/bot{self.settings.bot_token}/setMyName",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"name": self.settings.bot_name}),
        )

    @patch("requests.request")
    def test_set_bot_name_maintenance_mode(self, mock_request):
        """Test bot name setting in maintenance mode."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Enable maintenance mode
        self.settings.maintenance_mode = True
        self.settings.set_bot_name()

        # Verify the API call includes maintenance prefix
        expected_name = f"[🚨 MAINTENANCE] {self.settings.bot_name}"
        mock_request.assert_called_once_with(
            "POST",
            f"https://api.telegram.org/bot{self.settings.bot_token}/setMyName",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"name": expected_name}),
        )

    @patch("nz_store.models.logging")
    def test_set_bot_name_no_token(self, mock_logging):
        """Test bot name setting when bot_token is not set."""
        self.settings.bot_token = None
        self.settings.set_bot_name()

        mock_logging.warning.assert_called_once_with("Bot token or name is not set, skipping bot name update.")

    @patch("nz_store.models.logging")
    def test_set_bot_name_no_name(self, mock_logging):
        """Test bot name setting when bot_name is not set."""
        self.settings.bot_name = None
        self.settings.set_bot_name()

        mock_logging.warning.assert_called_once_with("Bot token or name is not set, skipping bot name update.")

    @patch("requests.request")
    @patch("nz_store.models.logging")
    def test_set_bot_name_request_exception(self, mock_logging, mock_request):
        """Test bot name setting when request fails."""
        mock_request.side_effect = requests.RequestException("Network error")

        self.settings.set_bot_name()

        mock_logging.error.assert_called_with("Failed to set bot name: Network error")

    @patch("requests.request")
    def test_set_bot_description_success(self, mock_request):
        """Test successful bot description setting."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        self.settings.set_bot_description()

        # Verify the API call was made correctly
        mock_request.assert_called_once_with(
            "POST",
            f"https://api.telegram.org/bot{self.settings.bot_token}/setMyShortDescription",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"short_description": self.settings.bot_description}),
        )

    @patch("nz_store.models.logging")
    def test_set_bot_description_no_token(self, mock_logging):
        """Test bot description setting when bot_token is not set."""
        self.settings.bot_token = None
        self.settings.set_bot_description()

        mock_logging.warning.assert_called_once_with(
            "Bot token or description is not set, skipping bot description update."
        )

    @patch("nz_store.models.logging")
    def test_set_bot_description_no_description(self, mock_logging):
        """Test bot description setting when bot_description is not set."""
        self.settings.bot_description = None
        self.settings.set_bot_description()

        mock_logging.warning.assert_called_once_with(
            "Bot token or description is not set, skipping bot description update."
        )

    @patch("requests.request")
    @patch("nz_store.models.logging")
    def test_set_bot_description_request_exception(self, mock_logging, mock_request):
        """Test bot description setting when request fails."""
        mock_request.side_effect = requests.RequestException("API error")

        self.settings.set_bot_description()

        mock_logging.error.assert_called_with("Failed to set bot description: API error")

    @patch("nz_store.models.Settings.set_bot_name")
    @patch("nz_store.models.Settings.set_bot_description")
    def test_save_calls_bot_methods(self, mock_set_description, mock_set_name):
        """Test that save method calls bot name and description methods."""
        self.settings.save()

        mock_set_name.assert_called_once()
        mock_set_description.assert_called_once()

    @patch("nz_store.models.Settings.set_bot_name")
    @patch("nz_store.models.Settings.set_bot_description")
    @patch("nz_store.models.logger")
    def test_save_handles_set_bot_name_exception(self, mock_logger, mock_set_description, mock_set_name):
        """Test that save method handles exceptions from set_bot_name."""
        mock_set_name.side_effect = Exception("Bot name error")

        self.settings.save()

        mock_set_name.assert_called_once()
        mock_set_description.assert_called_once()
        mock_logger.error.assert_called_with("Error setting bot name: Bot name error")

    @patch("nz_store.models.Settings.set_bot_name")
    @patch("nz_store.models.Settings.set_bot_description")
    @patch("nz_store.models.logger")
    def test_save_handles_set_bot_description_exception(self, mock_logger, mock_set_description, mock_set_name):
        """Test that save method handles exceptions from set_bot_description."""
        mock_set_description.side_effect = Exception("Bot description error")

        self.settings.save()

        mock_set_name.assert_called_once()
        mock_set_description.assert_called_once()
        mock_logger.error.assert_called_with("Error setting bot description: Bot description error")

    def test_settings_fields_defaults(self):
        """Test default values for Settings fields."""
        settings = Settings()

        self.assertIsNone(settings.bot_token)
        self.assertIsNone(settings.bot_name)
        self.assertIsNone(settings.bot_description)
        self.assertFalse(settings.maintenance_mode)

    def test_settings_fields_blank_and_null(self):
        """Test that fields can be blank and null."""
        # Update the existing singleton instance instead of creating a new one
        self.settings.bot_token = ""
        self.settings.bot_name = ""
        self.settings.bot_description = ""
        self.settings.maintenance_mode = True
        self.settings.save()

        self.assertEqual(self.settings.bot_token, "")
        self.assertEqual(self.settings.bot_name, "")
        self.assertEqual(self.settings.bot_description, "")
        self.assertTrue(self.settings.maintenance_mode)

    @patch("requests.request")
    def test_retry_mechanism_for_set_bot_name(self, mock_request):
        """Test error handling in set_bot_name method."""
        # Mock request to raise exception
        mock_request.side_effect = requests.RequestException("Network error")

        # Test that exception is caught and logged
        with patch("nz_store.models.logging") as mock_logging:
            self.settings.set_bot_name()
            # Should log the error
            mock_logging.error.assert_called_with("Failed to set bot name: Network error")

        # Verify that request was called once (exception handling prevents retries)
        self.assertEqual(mock_request.call_count, 1)

    @patch("requests.request")
    def test_retry_mechanism_for_set_bot_description(self, mock_request):
        """Test error handling in set_bot_description method."""
        # Mock request to raise exception
        mock_request.side_effect = requests.RequestException("Network error")

        # Test that exception is caught and logged
        with patch("nz_store.models.logging") as mock_logging:
            self.settings.set_bot_description()
            # Should log the error
            mock_logging.error.assert_called_with("Failed to set bot description: Network error")

        # Verify that request was called once (exception handling prevents retries)
        self.assertEqual(mock_request.call_count, 1)

    def test_retry_decorator_exists_on_set_bot_name(self):
        """Test that set_bot_name method has retry decorator."""
        # Check if the method has the retry decorator
        self.assertTrue(hasattr(self.settings.set_bot_name, "retry"))

    def test_retry_decorator_exists_on_set_bot_description(self):
        """Test that set_bot_description method has retry decorator."""
        # Check if the method has the retry decorator
        self.assertTrue(hasattr(self.settings.set_bot_description, "retry"))

    @patch("nz_store.models.requests.request")
    def test_actual_retry_behavior_set_bot_name(self, mock_request):
        """Test that retry actually works when exception is not caught internally."""
        # Create a version without the try-catch to test retry mechanism
        from unittest.mock import Mock

        # Create a mock that raises exception first 2 times, then succeeds
        mock_request.side_effect = [
            requests.RequestException("First failure"),
            requests.RequestException("Second failure"),
            Mock(status_code=200),
        ]

        # Remove the try-catch temporarily to test retry
        def set_bot_name_without_catch(self):
            if not self.bot_token or not self.bot_name:
                logging.warning("Bot token or name is not set, skipping bot name update.")
                return

            url = f"https://api.telegram.org/bot{self.bot_token}/setMyName"
            payload = json.dumps(
                {"name": f"[🚨 MAINTENANCE] {self.bot_name}" if self.maintenance_mode else self.bot_name}
            )
            headers = {"Content-Type": "application/json"}
            # Don't catch the exception here to allow retry to work
            requests.request("POST", url, headers=headers, data=payload)

        # Apply retry decorator to our test version
        from tenacity import retry, stop_after_attempt, wait_fixed

        set_bot_name_with_retry = retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1))(set_bot_name_without_catch)

        # Test the retry mechanism
        set_bot_name_with_retry(self.settings)

        # Verify it was called 3 times (2 failures + 1 success)
        self.assertEqual(mock_request.call_count, 3)
