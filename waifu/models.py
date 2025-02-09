import random

import requests
from django.conf import settings
from django.db import models

from models.base import BaseTelegramUserModel


class Image(models.Model):
    image_id = models.CharField(max_length=50)
    original_image = models.CharField(max_length=500, blank=True)
    thumbnail = models.CharField(max_length=500, blank=True)

    is_nsfw = models.BooleanField(default=False)

    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    creator_name = models.CharField(max_length=255, blank=True, default="")
    creator_username = models.CharField(max_length=255, blank=True, default="")
    caption = models.TextField(blank=True, default="")
    source = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.image_id}"


class TelegramUser(BaseTelegramUserModel):
    BOT_TOKEN = settings.WAIFU_TELEGRAM_BOT_TOKEN


class DiscordWebhook(models.Model):
    server_name = models.CharField(max_length=255, blank=True)
    webhook_url = models.URLField()
    interval = models.IntegerField(default=5)
    is_enabled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.server_name}"

    def send_image(self, image_url: str, is_nsfw: bool, creator_name: str):
        """Send image to discord server"""

        # read image as file object
        file = requests.get(
            image_url,
            stream=True,
            timeout=5,
        ).raw

        files = {"NKS2D-waifu.jpg" if is_nsfw is False else "SPOILER_NKS2D-waifu.jpg": file}
        payload = {
            "content": f"{'Artist: ' + creator_name if creator_name != '' else ''}",
            "username": random.choice(
                [
                    "Random Waifu",
                ]
            ),
            "avatar_url": image_url,
        }

        requests.post(
            self.webhook_url,
            data=payload,
            files=files,
        )
