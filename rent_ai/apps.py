from django.apps import AppConfig


class RentAiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rent_ai"

    def ready(self):
        import rent_ai.signals  # noqa: F401
