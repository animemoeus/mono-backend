from django.urls import path

from .views import RandomWaifuView, TelegramUserWebhook, WaifuDetailView, WaifuListView, WaifuSimilarImagesView

urlpatterns = [
    path("", WaifuListView.as_view(), name="index"),
    path("random/", RandomWaifuView.as_view(), name="random"),
    path("telegram-webhook/", TelegramUserWebhook.as_view(), name="telegram-webhook"),
    path("<str:image_id>/similar/", WaifuSimilarImagesView.as_view(), name="similar"),
    path("<str:image_id>/", WaifuDetailView.as_view(), name="detail"),
]

app_name = "waifu"
