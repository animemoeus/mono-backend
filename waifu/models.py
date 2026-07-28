import base64
import random
from io import BytesIO

import requests
from django.conf import settings
from django.db import models
from PIL import Image as PILImage

from models.base import BaseTelegramUserModel


class Image(models.Model):
    image_id = models.CharField(max_length=50)
    original_image = models.CharField(max_length=500, blank=True)
    thumbnail = models.CharField(max_length=500, blank=True)
    blur_data_url = models.TextField(blank=True, default="")  # base64 string

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

    def generate_blur_data_url(self):
        """
        Generates a blurred data URL from the original image.
        This method retrieves the original image from the URL stored in the model,
        resizes it to 2% of its original dimensions, converts it to a base64 string,
        and saves it to the blur_data_url field.
        The method includes the following steps:
        1. Obtain the image URL, refreshing if expired
        2. Fetch the image content from the URL
        3. Resize the image to 2% of its original size
        4. Convert the resized image to a base64 string
        5. Save the base64 string to the model's blur_data_url field
        Raises:
            requests.exceptions.RequestException: If there's an error fetching the image
            IOError: If there's an error processing the image
        """

        print("Generating blur data URL for image:", self.image_id)
        from waifu.utils import refresh_expired_urls

        # Get the image URL
        image_url = self.original_image
        if refresh_expired_urls([self.original_image]).get(self.original_image):
            image_url = refresh_expired_urls([self.original_image]).get(self.original_image)

        # Fetch the image from URL using requests
        response = requests.get(image_url)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Open the image from the response content
        img = PILImage.open(BytesIO(response.content))

        # Calculate new dimensions (2% of original size)
        width, height = img.size
        new_width = int(width * 0.02)
        new_height = int(height * 0.02)

        # Resize the image
        resized_img = img.resize((new_width, new_height))

        # Convert to base64
        buffer = BytesIO()
        img_format = img.format or "JPEG"
        resized_img.save(buffer, format=img_format)
        base64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Save the base64 string to the model
        self.blur_data_url = base64_string
        self.save()

    def generate_blur_data_url_task(self):
        """
        Generates a blurred data URL from the original image using a Celery task.
        This method calls the generate_blur_data_url method as a Celery task.
        """

        from waifu.tasks import waifu_generate_blur_data_url

        waifu_generate_blur_data_url.delay(self.image_id)


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
