from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from unfold.admin import ModelAdmin

from .models import SavedTiktokVideo, TiktokMonitor, User


@admin.register(User)
class UserAdmin(ModelAdmin):
    change_form_template = "tiktok/admin_edit_form.html"
    readonly_fields = (
        "nickname",
        "user_id",
        "avatar_url",
        "followers",
        "following",
        "visible_content_count",
        "created_at",
        "updated_at",
    )
    list_display = [
        "username",
        "nickname",
        "following",
        "followers",
        "visible_content_count",
        "created_at",
        "updated_at",
    ]
    search_fields = ("username", "nickname")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "nickname", "avatar_url", "avatar_file")}),
        (
            "User Info",
            {"fields": ("user_id", "followers", "following", "visible_content_count")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def response_change(self, request, obj):
        if "_update-information-from-api" in request.POST:
            print("Updating data from API")
            self.handle_update_data_from_api(request, obj)
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def handle_update_data_from_api(self, request, obj):
        try:
            obj.update_data_from_api()
            self.message_user(request, "Successfully updated user data from API.")
        except Exception as e:
            pass
            self.message_user(
                request,
                "Failed to update user data from the API.",
                level=messages.ERROR,
            )
            self.message_user(request, e, level=messages.ERROR)


@admin.register(TiktokMonitor)
class TiktokMonitorAdmin(ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    list_display = ["username", "created_at", "updated_at", "enabled"]
    search_fields = ("username",)


@admin.register(SavedTiktokVideo)
class SavedTiktokVideoAdmin(ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
