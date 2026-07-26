from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "core.users"
    verbose_name = _("Users")

    def ready(self):
        try:  # noqa: SIM105
            import core.users.signals  # noqa: F401, PLC0415
        except ImportError:
            pass
