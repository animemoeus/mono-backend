from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import Serializer

from backend.utils.telegram import validate_telegram_mini_app_data

from .models import TelegramUser


class ValidateTelegramMiniAppDataSerializer(Serializer):
    init_data = serializers.CharField(required=True)

    def validate_init_data(self, value):
        try:
            mini_app_data = validate_telegram_mini_app_data(value, settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN)
            self.create_or_update_telegram_user(mini_app_data)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        return value

    def create_or_update_telegram_user(self, telegram_user_data: dict):
        telegram_user, _ = TelegramUser.objects.get_or_create(
            user_id=telegram_user_data.get("id"),
            defaults={
                "first_name": telegram_user_data.get("first_name"),
                "last_name": telegram_user_data.get("last_name"),
                "username": telegram_user_data.get("username"),
            },
        )

        telegram_user.is_active = True
        telegram_user.first_name = telegram_user_data.get("first_name")
        telegram_user.last_name = telegram_user_data.get("last_name") or ""
        telegram_user.username = telegram_user_data.get("username") or ""
        telegram_user.request_count += 1
        telegram_user.save()
