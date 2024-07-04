import uuid

import requests
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from rest_framework import status

from .utils import InstagramAPI, user_profile_picture_upload_location


class User(models.Model):
    username = models.CharField(max_length=150, primary_key=True)
    full_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.FileField(upload_to=user_profile_picture_upload_location, blank=True, null=True)
    profile_picture_url = models.URLField(max_length=500)
    biography = models.TextField(blank=True)

    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    api_updated_time = models.DateTimeField(verbose_name="API Updated Time", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username}"

    def get_information_from_api(self) -> tuple[int, dict]:
        """
        Get Instagram user information from the API

        Returns:
            tuple[int, dict]: A tuple containing the HTTP status code and the user information.
        """

        api_client = InstagramAPI()
        status_code, user_info = api_client.get_user_info_v2(self.username)

        if status_code != status.HTTP_200_OK:
            return status_code, {}

        self.api_updated_time = timezone.now()
        self.save()

        return status_code, user_info

    def update_information_from_api(self) -> int:
        status_code, user_info = self.get_information_from_api()
        if status_code != status.HTTP_200_OK:
            return status_code

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

        self.api_updated_time = timezone.now()
        self.save()

        return status_code

    def get_user_stories(self) -> list:
        api_client = InstagramAPI()
        status_code, raw_stories = api_client.get_user_stories(self.username)

        if status_code != status.HTTP_200_OK:
            return

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

    def save_from_url_to_file_field(self, field_name: str, file_format: str, file_url: str) -> None:
        response = requests.get(file_url, timeout=30)

        if not response.status_code == status.HTTP_200_OK:
            return

        if hasattr(self, field_name):
            getattr(self, field_name).save(f"{uuid.uuid4()}.{file_format}", ContentFile(response.content))


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story_id = models.CharField(max_length=50)
    thumbnail_url = models.URLField(max_length=1000)
    media_url = models.URLField(max_length=1000, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    story_created_at = models.DateTimeField()

    # def __str__(self):
    #     return f"{self.user.username} - {self.story_id}"
