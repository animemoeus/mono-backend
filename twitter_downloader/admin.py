from django.contrib import admin
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin

from .models import DownloadedTweet, ExternalLink
from .models import Settings as TwitterDownloaderSettings
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    list_display = (
        "user_id",
        "first_name",
        "last_name",
        "username",
        "is_active",
        "is_banned",
    )
    readonly_fields = (
        "user_id",
        "first_name",
        "last_name",
        "username",
        "created_at",
        "updated_at",
    )
    search_fields = ("user_id", "first_name", "last_name", "username")


@admin.register(DownloadedTweet)
class DownloadedTweetAdmin(ModelAdmin):
    list_display = ("tweet_url", "telegram_user", "created_at")
    readonly_fields = ("tweet_url", "telegram_user", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False


@admin.register(ExternalLink)
class ExternalLinkAdmin(ModelAdmin):
    list_display = (
        "title",
        "url",
        "counter",
        "is_web_app",
        "is_active",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("counter", "created_at", "updated_at")
    ordering = ("-id",)


@admin.register(TwitterDownloaderSettings)
class TwitterDownloaderSettingsAdmin(SingletonModelAdmin, ModelAdmin):
    pass
