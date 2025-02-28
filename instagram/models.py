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
    profile_picture_url = models.URLField(max_length=500, help_text="The original profile picture URL from Instagram")
    biography = models.TextField(blank=True)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    allow_auto_update_stories = models.BooleanField(default=False)
    updated_from_api_datetime = models.DateTimeField(verbose_name="Update from API datetime", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.username}"

    def get_information_from_api(self) -> dict:
        api_client = InstagramAPI()

        if self.instagram_id:
            user_info = api_client.get_user_info_by_id_v2(self.instagram_id)
        else:
            user_info = api_client.get_user_info_v2(self.username)

        if not user_info:
            raise Exception("Cannot get user information from Instagram API")

        return user_info

    def update_information_from_api(self) -> Self:
        user_info = self.get_information_from_api()

        if "pk" in user_info:
            self.instagram_id = user_info["pk"]

        if "username" in user_info:
            self.username = user_info["username"]

        if "full_name" in user_info:
            self.full_name = user_info["full_name"]

        if "biography" in user_info:
            self.biography = user_info["biography"]

        if "follower_count" in user_info:
            self.follower_count = user_info["follower_count"]

        if "following_count" in user_info:
            self.following_count = user_info["following_count"]

        if user_info.get("hd_profile_pic_url_info") and user_info.get("hd_profile_pic_url_info").get("url"):
            hd_profile_pic_url = user_info.get("hd_profile_pic_url_info").get("url")

            # Check if the profile picture url is empty and update the file field
            if not self.profile_picture_url:
                self.profile_picture_url = hd_profile_pic_url
                self.save_from_url_to_file_field("profile_picture", "jpg", self.profile_picture_url)

            # Check if the profile picture is empty and update the file field
            if not self.profile_picture and self.profile_picture_url:
                self.save_from_url_to_file_field("profile_picture", "jpg", hd_profile_pic_url)

            # Check if the profile picture URL has changed and update the profile picture field
            if self.profile_picture_url.split("?")[0] != hd_profile_pic_url.split("?")[0]:
                self.save_from_url_to_file_field("profile_picture", "jpg", hd_profile_pic_url)

            self.profile_picture_url = hd_profile_pic_url

        self.updated_from_api_datetime = timezone.now()
        self.save()

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

    def save_from_url_to_file_field(self, field_name: str, file_format: str, file_url: str) -> None:
        response = requests.get(file_url, timeout=30)

        if not response.status_code == status.HTTP_200_OK:
            return

        if hasattr(self, field_name):
            getattr(self, field_name).save(f"{uuid.uuid4()}.{file_format}", ContentFile(response.content))


class Story(models.Model):
    class Meta:
        verbose_name = "Story"
        verbose_name_plural = "Stories"

    story_id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thumbnail_url = models.URLField(max_length=1000)
    media_url = models.URLField(max_length=1000, blank=True)

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
