import json
import logging
import uuid

import requests
from django.core.validators import FileExtensionValidator
from django.db import models
from simple_history.models import HistoricalRecords
from solo.models import SingletonModel
from tenacity import retry, stop_after_attempt, wait_fixed

from .utils import get_product_image_upload_path

logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(
        upload_to=get_product_image_upload_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
        help_text="Product image (max 5MB, jpg/jpeg/png/webp only)",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    @property
    def available_stock(self):
        """Returns the count of available (not sold) account stocks"""
        return self.account_stocks.filter(is_sold=False).count()

    def sync_stock_with_accounts(self):
        """Sync the stock field with available account stocks"""
        self.stock = self.available_stock
        self.save(update_fields=["stock"])


class AccountStock(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="account_stocks")
    email = models.EmailField(
        default="",
        max_length=255,
    )
    username = models.CharField(default="", max_length=255)
    password = models.CharField(default="", max_length=255)
    description = models.TextField(default="")
    is_sold = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.product.name} - {self.email}  {self.username}"


class TelegramUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    telegram_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    ORDER_STATUS_PENDING = "PENDING"
    ORDER_STATUS_COMPLETED = "COMPLETED"
    ORDER_STATUS_CANCELLED = "CANCELLED"
    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_PENDING, "Pending"),
        (ORDER_STATUS_COMPLETED, "Completed"),
        (ORDER_STATUS_CANCELLED, "Cancelled"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    account_stock = models.ForeignKey(AccountStock, on_delete=models.CASCADE, related_name="orders")
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.uuid} - {self.product.name} ({self.status})"


class Settings(SingletonModel):
    bot_token = models.CharField(max_length=255, blank=True, null=True)
    bot_name = models.CharField(max_length=255, blank=True, null=True)
    bot_description = models.TextField(blank=True, null=True)
    maintenance_mode = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return "Settings"

    def save(self, *args, **kwargs):
        try:
            self.set_bot_name()
        except Exception as e:
            logger.error(f"Error setting bot name: {e}")

        try:
            self.set_bot_description()
        except Exception as e:
            logger.error(f"Error setting bot description: {e}")

        super().save(*args, **kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def set_bot_name(self):
        """
        Sets the name of the Telegram bot using the Telegram Bot API.
        This method sends a POST request to the Telegram Bot API's setMyName endpoint
        to update the bot's display name. The method requires both bot_token and
        bot_name to be set on the instance.
        Returns:
            None
        Raises:
            None: Exceptions are caught and logged rather than raised.
        Notes:
            - If bot_token or bot_name is not set, the method logs a warning and returns early
            - Network errors and API failures are caught and logged as errors
            - No return value or exception is raised on failure
        """

        if not self.bot_token or not self.bot_name:
            logging.warning("Bot token or name is not set, skipping bot name update.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/setMyName"
        payload = json.dumps({"name": f"[🚨 MAINTENANCE] {self.bot_name}" if self.maintenance_mode else self.bot_name})
        headers = {"Content-Type": "application/json"}

        try:
            requests.request("POST", url, headers=headers, data=payload)
        except requests.RequestException as e:
            logging.error(f"Failed to set bot name: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def set_bot_description(self):
        """
        Set the short description of a Telegram bot using the Telegram Bot API.
        This method uses the bot_token attribute to authenticate with the Telegram API
        and sets the bot_description as the bot's short description. If either the
        bot_token or bot_description attribute is not set, a warning is logged and
        the method exits without making an API call.
        Returns:
            None
        Side effects:
            - Makes HTTP POST request to the Telegram API
            - Logs warnings if token or description is missing
            - Logs errors if the API request fails
        """

        if not self.bot_token or not self.bot_description:
            logging.warning("Bot token or description is not set, skipping bot description update.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/setMyShortDescription"
        payload = json.dumps({"short_description": self.bot_description})
        headers = {"Content-Type": "application/json"}

        try:
            requests.request("POST", url, headers=headers, data=payload)
        except requests.RequestException as e:
            logging.error(f"Failed to set bot description: {e}")
