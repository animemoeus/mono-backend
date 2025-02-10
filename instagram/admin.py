from django.contrib import admin, messages
from django.http import HttpResponseRedirect

from .models import RoastingLog, Story, User, UserFollower, UserFollowing
from .tasks import update_user_follower, update_user_following


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    change_form_template = "instagram/admin_edit_form.html"

    search_fields = ("username",)
    list_display = (
        "username",
        "updated_from_api_datetime",
        "allow_auto_update_stories",
        "created_at",
        "updated_at",
        "follower_count",
        "following_count",
    )
    readonly_fields = (
        "instagram_id",
        "full_name",
        "biography",
        "profile_picture_url",
        "follower_count",
        "following_count",
        "updated_from_api_datetime",
        "created_at",
        "updated_at",
    )
    ordering = ("username",)

    def response_change(self, request, obj: User):
        if "_update-information-from-api" in request.POST:
            self.handle_update_information_from_api(request, obj)
            return HttpResponseRedirect(".")

        if "_update-stories-from-api" in request.POST:
            self.handle_update_user_stories(request, obj)
            return HttpResponseRedirect(".")

        if "_update-follower-from-api" in request.POST:
            self.handle_update_user_follower(request, obj)
            return HttpResponseRedirect(".")

        if "_update-following-from-api" in request.POST:
            self.handle_update_user_following(request, obj)
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def handle_update_information_from_api(self, request, obj: User):
        try:
            obj.update_information_from_api()
            self.message_user(request, "Successfully get information from API")
        except Exception as e:
            self.message_user(request, "Failed to get information from the API", level=messages.ERROR)
            self.message_user(request, e, level=messages.ERROR)

    def handle_update_user_stories(self, request, obj: User):
        stories, saved_stories = obj.update_user_stories()
        self.message_user(request, f"{len(saved_stories)}/{len(stories)} stories updated")

    def handle_update_user_follower(self, request, obj: User):
        update_user_follower.delay(obj.instagram_id)
        self.message_user(request, "User follower updated")

    def handle_update_user_following(self, request, obj: User):
        update_user_following.delay(obj.instagram_id)
        self.message_user(request, "User following updated")


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("user", "story_id", "created_at", "story_created_at")
    readonly_fields = ["story_id", "created_at", "story_created_at"]
    search_fields = ("user", "story_id")
    ordering = ("-story_created_at",)


@admin.register(UserFollower)
class UserFollowerAdmin(admin.ModelAdmin):
    list_display = ["username", "full_name", "user", "is_private_account", "created_at"]
    readonly_fields = [
        "profile_picture",
        "created_at",
    ]

    search_fields = ["user__username"]


@admin.register(UserFollowing)
class UserFollowingAdmin(admin.ModelAdmin):
    list_display = ["username", "full_name", "user", "is_private_account", "created_at"]
    readonly_fields = [
        "profile_picture",
        "created_at",
    ]
    search_fields = ["user__username"]


@admin.register(RoastingLog)
class RoastingLogAdmin(admin.ModelAdmin):
    list_display = ("username", "created_at")
    readonly_fields = ("username", "roasting_text", "user_data", "created_at")
    search_fields = ("username",)
    ordering = ("-created_at",)
