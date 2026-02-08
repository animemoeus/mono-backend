from django.contrib import admin
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import BroadcastLog, BroadcastMessage, DownloadedTweet, ExternalLink
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


@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(ModelAdmin):
    list_display = (
        "message_preview",
        "status_badge",
        "total_users",
        "sent_count",
        "failed_count",
        "progress_bar",
        "created_at",
        "started_at",
    )
    list_filter = ("status", "created_at", "started_at")
    search_fields = ("message",)
    readonly_fields = (
        "status",
        "total_users",
        "sent_count",
        "failed_count",
        "created_at",
        "started_at",
        "completed_at",
        "created_by",
    )
    ordering = ("-created_at",)

    fieldsets = (
        ("Message", {"fields": ("message",)}),
        (
            "Status & Statistics",
            {
                "fields": (
                    "status",
                    "total_users",
                    "sent_count",
                    "failed_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "started_at",
                    "completed_at",
                )
            },
        ),
        ("Audit", {"fields": ("created_by",)}),
    )

    @admin.display(description="Message")
    def message_preview(self, obj):
        """Show first 50 characters of message"""
        preview = obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
        return preview

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            "draft": "gray",
            "sending": "blue",
            "completed": "green",
            "failed": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Progress")
    def progress_bar(self, obj):
        """Display progress bar for broadcast"""
        if obj.total_users == 0:
            return "-"

        _ = (obj.sent_count + obj.failed_count) / obj.total_users * 100
        success_percent = obj.sent_count / obj.total_users * 100 if obj.total_users > 0 else 0
        failed_percent = obj.failed_count / obj.total_users * 100 if obj.total_users > 0 else 0

        return format_html(
            '<div style="width: 200px; background-color: #e0e0e0; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: #4caf50; height: 20px; float: left;"></div>'
            '<div style="width: {}%; background-color: #f44336; height: 20px; float: left;"></div>'
            "</div>"
            '<div style="clear: both; font-size: 11px; margin-top: 2px;">{}% sent, {}% failed</div>',
            success_percent,
            failed_percent,
            f"{success_percent:.1f}",
            f"{failed_percent:.1f}",
        )

    def save_model(self, request, obj, form, change):
        """Auto-fill created_by field with current user"""
        if not change:  # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @action(description="Start Broadcasting")
    def start_broadcast(self, request, queryset):
        """Admin action to start broadcasting selected messages"""
        count = 0
        for broadcast in queryset:
            if broadcast.status == BroadcastMessage.BroadcastStatus.DRAFT:
                broadcast.start_broadcast()
                count += 1

        self.message_user(
            request,
            f"Started broadcasting {count} message(s). Check celery logs for progress.",
        )

    actions = [start_broadcast]


@admin.register(BroadcastLog)
class BroadcastLogAdmin(ModelAdmin):
    list_display = (
        "telegram_user_info",
        "broadcast_preview",
        "status_badge",
        "sent_at",
    )
    list_filter = ("status", "sent_at", "broadcast")
    search_fields = (
        "telegram_user__user_id",
        "telegram_user__username",
        "telegram_user__first_name",
        "telegram_user__last_name",
    )
    readonly_fields = (
        "broadcast",
        "telegram_user",
        "status",
        "error_message",
        "sent_at",
    )
    ordering = ("-sent_at",)

    @admin.display(description="Telegram User")
    def telegram_user_info(self, obj):
        """Display telegram user information"""
        name = obj.telegram_user.username or f"{obj.telegram_user.first_name} {obj.telegram_user.last_name}".strip()
        return f"{name} ({obj.telegram_user.user_id})"

    @admin.display(description="Broadcast Message")
    def broadcast_preview(self, obj):
        """Show preview of broadcast message"""
        preview = obj.broadcast.message[:40] + "..." if len(obj.broadcast.message) > 40 else obj.broadcast.message
        return preview

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display status with color badge"""
        color = "green" if obj.status == "success" else "red"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )


@admin.register(TwitterDownloaderSettings)
class TwitterDownloaderSettingsAdmin(SingletonModelAdmin, ModelAdmin):
    pass
