import base64
import logging
import random
from io import BytesIO

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from pgvector.django import VectorField
from PIL import Image as PILImage
from solo.models import SingletonModel

from models.base import BaseTelegramUserModel

logger = logging.getLogger(__name__)


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

    embedding = VectorField(dimensions=1536, blank=True, null=True)

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

    def generate_embedding(self, force: bool = False) -> list[float] | None:
        """
        Generates and saves the embedding vector for this image using OpenRouter.
        Skips the API call if an embedding already exists, unless force=True.
        """

        if self.embedding is not None and not force:
            return self.embedding

        from waifu.utils import refresh_expired_urls

        image_url = self.original_image
        refreshed_url = refresh_expired_urls([self.original_image]).get(self.original_image)
        if refreshed_url:
            image_url = refreshed_url

        embedding, _token_usage = generate_image_embedding(image_url)
        self.embedding = embedding
        self.save(update_fields=["embedding"])
        return self.embedding

    def generate_embedding_task(self, force: bool = False) -> None:
        """
        Generates the embedding for this image using a Celery task.
        """

        from waifu.tasks import waifu_generate_image_embedding

        waifu_generate_image_embedding.delay(self.image_id, force)


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


class Setting(SingletonModel):
    openrouter_base_url = models.URLField(default="https://openrouter.ai", max_length=5000)
    embedding_model = models.CharField(max_length=255, default="google/gemini-embedding-2")
    embedding_api_key = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Waifu Setting"


def get_waifu_embedding_api_key() -> str:
    setting = Setting.get_solo()
    if not setting.embedding_api_key:
        msg = "OpenRouter API key is not configured in Waifu settings"
        raise ImproperlyConfigured(msg)
    return setting.embedding_api_key


def generate_image_embedding(image_url: str) -> tuple[list[float], int]:
    """Generate embedding vector for an image using OpenRouter's embeddings API.

    Args:
        image_url: URL of the image to embed

    Returns:
        Tuple of (embedding vector, token_usage)

    Raises:
        ImproperlyConfigured: If the OpenRouter API key is not configured
        ValueError: If image_url is empty
        Exception: If the API request fails
    """
    if not image_url or not image_url.strip():
        msg = "Image URL cannot be empty for image embedding generation"
        raise ValueError(msg)

    setting = Setting.get_solo()
    api_key = get_waifu_embedding_api_key()
    base_url = f"{setting.openrouter_base_url.rstrip('/')}/api/v1/embeddings"
    model = setting.embedding_model

    try:
        response = requests.post(
            base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://animemoeus.com",
                "X-Title": "AnimeMoeUs Waifu",
            },
            json={
                "model": model,
                "input": [
                    {
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    },
                ],
                "encoding_format": "float",
                "dimensions": 1536,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        embedding = data["data"][0]["embedding"]
        token_usage = data.get("usage", {}).get("total_tokens", 0)

        logger.info(
            "Generated waifu image embedding with %d dimensions (tokens: %d)",
            len(embedding),
            token_usage,
        )

        return embedding, token_usage

    except Exception:
        logger.exception("Failed to generate waifu image embedding for URL %s", image_url)
        raise
