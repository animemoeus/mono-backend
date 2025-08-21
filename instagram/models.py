import uuid
from typing import Self

import requests
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework import status
from simple_history.models import HistoricalRecords

from .mixins import URLToFileFieldMixin
from .tasks import user_follower_update_profile_pictures, user_following_update_profile_pictures
from .utils import (
    InstagramAPI,
    user_follower_profile_picture_upload_location,
    user_following_profile_picture_upload_location,
    user_profile_picture_upload_location,
    user_stories_upload_location,
)


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instagram_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.FileField(upload_to=user_profile_picture_upload_location, blank=True, null=True)
    profile_picture_url = models.URLField(max_length=2500, help_text="The original profile picture URL from Instagram")
    biography = models.TextField(blank=True)
    is_private = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    media_count = models.PositiveIntegerField(default=0)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    # Field to store user auto-update limits
    auto_update_stories_limit_count = models.PositiveIntegerField(
        default=5, help_text="Free users can update stories up to this limit"
    )
    auto_update_profile_limit_count = models.PositiveIntegerField(
        default=5, help_text="Free users can update profile up to this limit"
    )

    allow_auto_update_stories = models.BooleanField(default=False)
    allow_auto_update_profile = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_at_from_api = models.DateTimeField(verbose_name="Updated From API", blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.username}"

    def get_information_from_api(self) -> dict:
        api_client = InstagramAPI()

        data = {}

        if self.instagram_id:
            user_info = api_client.get_user_info_by_id(self.instagram_id)
            data["full_name"] = user_info.get("full_name")
            data["username"] = user_info.get("username")
            data["is_private"] = user_info.get("is_private")
            data["is_verified"] = user_info.get("is_verified")
            data["biography"] = user_info.get("biography")
            data["follower_count"] = (
                user_info.get("edge_followed_by").get("count")
                if user_info.get("edge_followed_by") and user_info.get("edge_followed_by").get("count")
                else 0
            )
            data["following_count"] = (
                user_info.get("edge_follow").get("count")
                if user_info.get("edge_follow") and user_info.get("edge_follow").get("count")
                else 0
            )
            data["media_count"] = (
                user_info.get("edge_owner_to_timeline_media").get("count")
                if user_info.get("edge_owner_to_timeline_media")
                and user_info.get("edge_owner_to_timeline_media").get("count")
                else 0
            )
            data["profile_pic_url"] = (
                user_info.get("profile_pic_url_hd")
                if user_info.get("profile_pic_url_hd")
                else user_info.get("profile_pic_url")
            )
            data["raw"] = user_info

        else:
            user_info = api_client.get_user_info_v2(self.username)
            data["pk"] = user_info.get("pk")
            data["full_name"] = user_info.get("full_name")
            data["username"] = user_info.get("username")
            data["is_private"] = user_info.get("is_private")
            data["is_verified"] = user_info.get("is_verified")
            data["biography"] = user_info.get("biography")
            data["follower_count"] = user_info.get("follower_count")
            data["following_count"] = user_info.get("following_count")
            data["media_count"] = user_info.get("media_count")
            data["profile_pic_url"] = (
                user_info.get("hd_profile_pic_url_info").get("url")
                if user_info.get("hd_profile_pic_url_info") and user_info.get("hd_profile_pic_url_info").get("url")
                else user_info.get("profile_pic_url")
            )
            data["raw"] = user_info

        if not user_info:
            raise Exception("Cannot get user information from Instagram API")

        return data

    def update_information_from_api(self) -> Self:
        # Get user information from API
        user_info = self.get_information_from_api()

        # Map API fields to model fields
        field_mapping = {
            "pk": "instagram_id",
            "username": "username",
            "full_name": "full_name",
            "biography": "biography",
            "is_private": "is_private",
            "is_verified": "is_verified",
            "follower_count": "follower_count",
            "following_count": "following_count",
            "media_count": "media_count",
            "profile_pic_url": "profile_picture_url",
        }

        # Update fields if they exist in user_info
        for api_field, model_field in field_mapping.items():
            if api_field in user_info:
                setattr(self, model_field, user_info[api_field])

        # Save profile picture if it exists in user_info
        if self.profile_picture_url:
            self.save_from_url_to_file_field(
                "profile_picture", "jpg", self.profile_picture_url, save=False
            )  # Ensure save=False to avoid multiple history records

        # Save all changes at once to create a single history entry
        self.updated_at_from_api = timezone.now()
        self.save()

        # Decrement the counter if user has a limit count
        if self.auto_update_profile_limit_count > 0:
            self.auto_update_profile_limit_count -= 1
            self.save(update_fields=["auto_update_profile_limit_count"])

        return self

    def get_user_stories(self) -> list:
        api_client = InstagramAPI()
        status_code, raw_stories = api_client.get_user_stories(self.username)

        if status_code != status.HTTP_200_OK:
            return []

        stories = []
        for story in raw_stories:
            stories.append(
                {
                    "story_id": story.get("id"),
                    "thumbnail_url": story.get("thumbnail_url_original"),
                    "media_url": story.get("video_url_original") or story.get("thumbnail_url_original"),
                    "created_at": story.get("taken_at_date"),
                }
            )

        return stories

    def update_user_stories(self) -> tuple[list, list]:
        stories = self.get_user_stories()
        saved_stories = []
        if not stories:
            return stories, saved_stories

        for story in stories:
            if Story.objects.filter(story_id=story["story_id"]).exists():
                continue
            else:
                x = Story.objects.create(
                    user=self,
                    story_id=story["story_id"],
                    thumbnail_url=story["thumbnail_url"],
                    media_url=story["media_url"],
                    story_created_at=story["created_at"],
                )
                saved_stories.append(x)

        # Decrement the counter if user has a limit count
        if self.auto_update_stories_limit_count > 0:
            self.auto_update_stories_limit_count -= 1
            self.save(update_fields=["auto_update_stories_limit_count"])

        return stories, saved_stories

    @transaction.atomic
    def update_user_follower(self):
        api_client = InstagramAPI()
        follower = api_client.get_user_followers(self.username)

        if follower:
            UserFollower.objects.filter(user=self).delete()

        user_follower_list = [
            UserFollower(
                user=self,
                instagram_id=user.get("id"),
                username=user.get("username"),
                full_name=user.get("full_name"),
                profile_picture_url=user.get("profile_pic_url"),
                is_private_account=user.get("is_private"),
            )
            for user in follower
        ]
        UserFollower.objects.bulk_create(user_follower_list)
        user_follower_update_profile_pictures.delay(self.instagram_id)

    @transaction.atomic
    def update_user_following(self):
        api_client = InstagramAPI()
        following = api_client.get_user_following(self.username)

        if following:
            UserFollowing.objects.filter(user=self).delete()

        user_following_list = [
            UserFollowing(
                user=self,
                instagram_id=user.get("id"),
                username=user.get("username"),
                full_name=user.get("full_name"),
                profile_picture_url=user.get("profile_pic_url"),
                is_private_account=user.get("is_private"),
            )
            for user in following
        ]
        UserFollowing.objects.bulk_create(user_following_list)
        user_following_update_profile_pictures.delay(self.instagram_id)

    def save_from_url_to_file_field(self, field_name: str, file_format: str, file_url: str, save: bool = True) -> None:
        response = requests.get(file_url, timeout=30)

        if not response.status_code == status.HTTP_200_OK:
            return

        if hasattr(self, field_name):
            getattr(self, field_name).save(
                f"{uuid.uuid4()}.{file_format}",
                ContentFile(response.content),
                save=save,
            )


class Story(models.Model):
    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    story_id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail_url = models.URLField(max_length=2500)
    media_url = models.URLField(max_length=2500, blank=True)

    thumbnail = models.ImageField(upload_to=user_stories_upload_location, blank=True, null=True)
    media = models.FileField(upload_to=user_stories_upload_location, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    story_created_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.story_id}"

    def save_from_url_to_file_field(self, field_name: str, file_format: str, file_url: str) -> None:
        response = requests.get(file_url, timeout=30)

        if not response.status_code == status.HTTP_200_OK:
            return

        if hasattr(self, field_name):
            getattr(self, field_name).save(f"{uuid.uuid4()}.{file_format}", ContentFile(response.content))


class UserFollower(models.Model, URLToFileFieldMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    instagram_id = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture_url = models.URLField(max_length=1000)
    profile_picture = models.FileField(upload_to=user_follower_profile_picture_upload_location, blank=True, null=True)
    is_private_account = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}"


class UserFollowing(models.Model, URLToFileFieldMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    instagram_id = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture_url = models.URLField(max_length=1000)
    profile_picture = models.FileField(upload_to=user_following_profile_picture_upload_location, blank=True, null=True)
    is_private_account = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}"


class RoastingLog(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255)
    user_data = models.JSONField()
    roasting_text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}"


@receiver(post_save, sender=Story)
def story_post_save(sender, instance, **kwargs):
    # Check if the thumbnail is empty and update the file field
    if not instance.thumbnail:
        instance.save_from_url_to_file_field("thumbnail", "jpg", instance.thumbnail_url)

    # Check if the media is empty and update the file field
    if not instance.media and instance.media_url:
        media_type = instance.media_url.split("?")[0].split(".")[-1]  # Should be jpg or mp4
        instance.save_from_url_to_file_field("media", media_type, instance.media_url)
