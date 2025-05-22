from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import DiscordWebhook, Image, TelegramUser

# from import_export.admin import ImportExportModelAdmin


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    list_display = ("image_id",)
    search_fields = ("image_id",)


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    pass


@admin.register(DiscordWebhook)
class DiscordWebhookAdmin(ModelAdmin):
    pass
