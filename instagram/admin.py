from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import RoastingLog, Story, User, UserFollower, UserFollowing
from .tasks import update_user_follower, update_user_following


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, ModelAdmin):
    search_fields = ("username", "full_name", "biography")
    list_display = (
        "username",
        "full_name",
        "is_private",
        "is_verified",
        "follower_count",
        "following_count",
        "media_count",
        "updated_at_from_api",
        "allow_auto_update_stories",
        "allow_auto_update_profile",
        "auto_update_stories_limit_count",
        "auto_update_profile_limit_count",
    )
    list_filter = ("is_private", "is_verified", "allow_auto_update_stories")
    readonly_fields = (
        "uuid",
        "instagram_id",
        "full_name",
        "biography",
        "profile_picture",
        "profile_picture_url",
        "is_private",
        "is_verified",
        "media_count",
        "follower_count",
        "following_count",
        "updated_at_from_api",
        "created_at",
        "updated_at",
    )
    ordering = ("username",)

    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "uuid",
                    "username",
                    "instagram_id",
                    "full_name",
                    "biography",
                    "profile_picture",
                    "profile_picture_url",
                )
            },
        ),
        (
            "Account Status",
            {
                "fields": (
                    "is_private",
                    "is_verified",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "media_count",
                    "follower_count",
                    "following_count",
                )
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "allow_auto_update_stories",
                    "allow_auto_update_profile",
                    "auto_update_stories_limit_count",
                    "auto_update_profile_limit_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "updated_at_from_api",
                )
            },
        ),
    )

    actions_detail = [
        {
            "title": "API Actions",
            "items": [
                "handle_update_information_from_api",
                "handle_update_stories",
                "handle_update_followers",
                "handle_update_following",
            ],
        },
    ]

    @action(description="Update Information")
    def handle_update_information_from_api(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)
            obj.update_information_from_api()
            self.message_user(request, "Successfully get information from API")
        except Exception as e:
            self.message_user(
                request,
                "Failed to get information from the API",
                level=messages.ERROR,
            )
            self.message_user(request, e, level=messages.ERROR)

        return redirect(reverse_lazy("admin:instagram_user_change", args=[object_id]))

    @action(description="Get Stories")
    def handle_update_stories(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)
            obj.update_user_stories()
            self.message_user(request, "Successfully get information from API")
        except Exception as e:
            self.message_user(
                request,
                "Failed to get information from the API",
                level=messages.ERROR,
            )
            self.message_user(request, e, level=messages.ERROR)

        return redirect(reverse_lazy("admin:instagram_user_change", args=[object_id]))

    @action(description="Update Followers")
    def handle_update_followers(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)
            update_user_follower.delay(obj.instagram_id)
            self.message_user(request, "Successfully get information from API")
        except Exception as e:
            self.message_user(
                request,
                "Failed to get information from the API",
                level=messages.ERROR,
            )
            self.message_user(request, e, level=messages.ERROR)

        return redirect(reverse_lazy("admin:instagram_user_change", args=[object_id]))

    @action(description="Update Following")
    def handle_update_following(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)
            update_user_following.delay(obj.instagram_id)
            self.message_user(request, "Successfully get information from API")
        except Exception as e:
            self.message_user(
                request,
                "Failed to get information from the API",
                level=messages.ERROR,
            )
            self.message_user(request, e, level=messages.ERROR)

        return redirect(reverse_lazy("admin:instagram_user_change", args=[object_id]))


@admin.register(Story)
class StoryAdmin(ModelAdmin):
    list_display = ("user", "story_id", "created_at", "story_created_at")
    readonly_fields = ["story_id", "created_at", "story_created_at"]
    search_fields = ("user", "story_id")
    ordering = ("-story_created_at",)


@admin.register(UserFollower)
class UserFollowerAdmin(ModelAdmin):
    list_display = ["username", "full_name", "user", "is_private_account", "created_at"]
    readonly_fields = [
        "profile_picture",
        "created_at",
    ]

    search_fields = ["user__username"]


@admin.register(UserFollowing)
class UserFollowingAdmin(ModelAdmin):
    list_display = ["username", "full_name", "user", "is_private_account", "created_at"]
    readonly_fields = [
        "profile_picture",
        "created_at",
    ]
    search_fields = ["user__username"]


@admin.register(RoastingLog)
class RoastingLogAdmin(ModelAdmin):
    list_display = ("username", "created_at")
    readonly_fields = ("username", "roasting_text", "user_data", "created_at")
    search_fields = ("username",)
    ordering = ("-created_at",)
