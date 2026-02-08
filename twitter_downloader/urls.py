from django.urls import path

from .views import SafelinkView, TelegramWebhookV2View, TelegramWebhookView, ValidateTelegramMiniAppDataView

urlpatterns = [
    path("safelink/", SafelinkView.as_view(), name="safelink"),
    path("telegram-webhook/", TelegramWebhookView.as_view(), name="telegram-webhook"),
    path(
        "telegram-webhook-v2/",
        TelegramWebhookV2View.as_view(),
        name="telegram-webhook-v2",
    ),
    path(
        "telegram-webhook/validate-mini-app-data/",
        ValidateTelegramMiniAppDataView.as_view(),
        name="validate-mini-app-data",
    ),
]

app_name = "twitter_downloader"
