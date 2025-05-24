from django.apps import AppConfig


class NzStoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nz_store"

    def ready(self):
        import nz_store.signals  # noqa: F401
