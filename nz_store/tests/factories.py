import factory
from django.utils import timezone
from factory import SubFactory

from nz_store.models import AccountStock, Order, Product, ProductCategory, Settings, TelegramUser


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for ProductCategory model."""

    class Meta:
        model = ProductCategory
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    description = factory.Faker("text", max_nb_chars=200)


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for Product model."""

    class Meta:
        model = Product

    category = SubFactory(ProductCategoryFactory)
    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=500)
    image = factory.django.ImageField(width=640, height=480, color="blue")
    price = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    stock = factory.Faker("random_int", min=0, max=1000)
    is_active = True  # Default to True to match model default


class TelegramUserFactory(factory.django.DjangoModelFactory):
    """Factory for TelegramUser model."""

    class Meta:
        model = TelegramUser
        django_get_or_create = ["telegram_id"]

    telegram_id = factory.LazyFunction(lambda: str(factory.Faker._get_faker().random.randint(100000000, 999999999)))
    username = factory.LazyAttribute(
        lambda obj: factory.Faker._get_faker().user_name() if factory.Faker._get_faker().boolean() else None
    )
    first_name = factory.Faker("first_name")
    last_name = factory.LazyAttribute(
        lambda obj: factory.Faker._get_faker().last_name() if factory.Faker._get_faker().boolean() else None
    )


class AccountStockFactory(factory.django.DjangoModelFactory):
    """Factory for AccountStock model."""

    class Meta:
        model = AccountStock

    product = SubFactory(ProductFactory)
    email = factory.Faker("email")
    username = factory.Faker("user_name")
    password = factory.Faker(
        "password",
        length=12,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    description = factory.Faker("text", max_nb_chars=300)
    is_sold = factory.Faker("boolean", chance_of_getting_true=30)  # 30% chance of being sold


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for Order model."""

    class Meta:
        model = Order

    product = SubFactory(ProductFactory)
    account_stock = SubFactory(AccountStockFactory)
    telegram_user = SubFactory(TelegramUserFactory)
    status = factory.Faker(
        "random_element",
        elements=[
            Order.ORDER_STATUS_PENDING,
            Order.ORDER_STATUS_COMPLETED,
            Order.ORDER_STATUS_CANCELLED,
        ],
    )
    paid_at = factory.LazyAttribute(lambda obj: timezone.now() if obj.status == Order.ORDER_STATUS_COMPLETED else None)

    @factory.post_generation
    def set_account_stock_for_product(self, create, extracted, **kwargs):
        """Ensure the account_stock belongs to the same product as the order."""
        if create and self.account_stock.product != self.product:
            # Create a new account stock for the correct product
            self.account_stock = AccountStockFactory(product=self.product)
            self.save()


class SettingsFactory(factory.django.DjangoModelFactory):
    """Factory for Settings model."""

    class Meta:
        model = Settings
        django_get_or_create = ["id"]  # Use singleton pattern

    id = 1  # Always use ID 1 for singleton
    bot_token = factory.Faker("sha256")
    bot_name = factory.Faker("company")
    bot_description = factory.Faker("text", max_nb_chars=200)
    maintenance_mode = factory.Faker("boolean", chance_of_getting_true=20)
