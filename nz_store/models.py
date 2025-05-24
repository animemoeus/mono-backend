import uuid

from django.db import models


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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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
