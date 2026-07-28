import uuid

import requests
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models


# TODO: move this function to a separate file
def tiktok_profile_picture_upload_location(instance, filename):
    return f"tiktok/user/{instance.username}/profile-picture/{filename}"


class User(models.Model):
    """Tiktok user model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255, unique=True)
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)
    visible_content_count = models.PositiveIntegerField(default=0)
    avatar_url = models.URLField(max_length=555)
    avatar_file = models.ImageField(upload_to=tiktok_profile_picture_upload_location, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    def clean(self):
        if self.username.startswith("@"):
            raise ValidationError("Username should not have `@` prefix")

    def save_from_url_to_file_field(self, field_name: str, file_format: str, file_url: str):
        response = requests.get(file_url, timeout=5)

        if not response.ok:
            return

        if hasattr(self, field_name):
            getattr(self, field_name).save(f"{uuid.uuid4()}.{file_format}", ContentFile(response.content))

    def update_data_from_api(self):
        from tiktok.utils import TikHubAPI

        tikhub = TikHubAPI()
        user_info = tikhub.get_user_info(self.username)

        self.nickname = user_info["nickname"]
        self.user_id = user_info["user_id"]
        self.followers = user_info["followers"]
        self.following = user_info["following"]
        self.visible_content_count = user_info["visible_content_count"]
        self.avatar_url = user_info["avatar"]

        self.save_from_url_to_file_field("avatar_file", "jpg", self.avatar_url)

        self.save()


class TiktokMonitor(models.Model):
    """Monitor specific TikTok user accounts posts"""

    username = models.CharField(max_length=255, help_text="Should have prefix `@`")
    enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class SavedTiktokVideo(models.Model):
    id = models.CharField(max_length=25, primary_key=True)
    tiktok_user = models.ForeignKey(TiktokMonitor, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
