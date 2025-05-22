from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from .models import RoastingLog, Story, User, UserFollower, UserFollowing
from .tasks import update_user_follower, update_user_following


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, ModelAdmin):
    change_form_template = "instagram/admin_edit_form.html"

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
            {"fields": ("allow_auto_update_stories", "allow_auto_update_profile")},
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

    def save_model(self, request, obj, form, change):
        """
        Override the default save_model method to conditionally skip model saving.
        This method examines the POST data to determine if the save action is part
        of an API update operation. If the request contains any of the API update
        flags (_update-information-from-api, _update-stories-from-api,
        _update-follower-from-api, _update-following-from-api), the save operation
        is skipped. Otherwise, it delegates to the parent class's save_model method.
        Parameters:
            request (HttpRequest): The request that triggered the save.
            obj (Model): The model instance to save.
            form (ModelForm): The form instance used to save the model.
            change (bool): True if this is a change to an existing object, False if it's a new object.
        Returns:
            None
        """

        if (
            "_update-information-from-api" in request.POST
            or "_update-stories-from-api" in request.POST
            or "_update-follower-from-api" in request.POST
            or "_update-following-from-api" in request.POST
        ):
            return

        super().save_model(request, obj, form, change)


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
