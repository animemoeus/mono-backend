import json

from django.test import TestCase

from backend.utils.telegram import TelegramWebhookParser


class TestTelegramWebhookParser(TestCase):
    def setUp(self):
        self.request_data_1 = json.dumps(
            {
                "update_id": 10000,
                "message": {
                    "date": 1441645532,
                    "chat": {"last_name": "Test Lastname", "id": 1111111, "first_name": "Test", "username": "Test"},
                    "message_id": 1365,
                    "from": {"last_name": "Tendean", "id": 1111111, "first_name": "Arter", "username": "artertendean"},
                    "text": "/start",
                },
            }
        )

    def test_get_user(self):
        webhook = TelegramWebhookParser(self.request_data_1)
        telegram_user = webhook.get_user()

        self.assertEqual(telegram_user.get("id"), 1111111)
        self.assertEqual(telegram_user.get("first_name"), "Arter")
        self.assertEqual(telegram_user.get("last_name"), "Tendean")
        self.assertEqual(telegram_user.get("username"), "artertendean")

    def test_get_text_message(self):
        webhook = TelegramWebhookParser(self.request_data_1)
        text_message = webhook.get_text_message()

        self.assertEqual(text_message, "/start")
