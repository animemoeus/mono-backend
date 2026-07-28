from django.urls import path

from .views import RandomWaifuView
from .views import TelegramUserWebhook
from .views import WaifuDetailView
from .views import WaifuListView

urlpatterns = [
    path("", WaifuListView.as_view(), name="index"),
    path("random/", RandomWaifuView.as_view(), name="random"),
    path("telegram-webhook/", TelegramUserWebhook.as_view(), name="telegram-webhook"),
    path("<str:image_id>/", WaifuDetailView.as_view(), name="detail"),
]

app_name = "waifu"
