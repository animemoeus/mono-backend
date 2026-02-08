from django.urls import path

from .views import SafelinkView, TelegramWebhookView, ValidateTelegramMiniAppDataView

urlpatterns = [
    path("safelink/", SafelinkView.as_view(), name="safelink"),
    path("telegram-webhook/", TelegramWebhookView.as_view(), name="telegram-webhook"),
    path(
        "telegram-webhook/validate-mini-app-data/",
        ValidateTelegramMiniAppDataView.as_view(),
        name="validate-mini-app-data",
    ),
]

app_name = "twitter_downloader"
