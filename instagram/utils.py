import requests
from django.conf import settings
from rest_framework import status


class InstagramAPI:
    def __init__(self):
        self.base_url = settings.INSTAGRAM_API_URL
        self.headers = {"Authorization": f"Bearer {settings.INSTAGRAM_API_KEY}"}

    def get_user_info_v2(self, username: str) -> tuple[int, dict]:
        """
        Get user information from Instagram API v2.

        Args:
            username: Instagram username.

        Returns:
            A tuple containing the HTTP status code and the response data.
        """

        url = self.base_url + "/api/v1/instagram/web_app/fetch_user_info_by_username_v2"
        params = {"username": username}
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        status_code = response.status_code

        response_data = {}
        if status_code == status.HTTP_200_OK:
            response = response.json()
            response_data = response.get("data")

        return status_code, response_data

    def get_user_stories(self, username: str) -> tuple[int, list]:
        url = self.base_url + "/api/v1/instagram/web_app/fetch_user_stories_by_username"
        params = {"username": username}
        response = requests.get(url, headers=self.headers, params=params, timeout=30)
        status_code = response.status_code

        response_data = {}
        if status_code == status.HTTP_200_OK:
            response = response.json()
            response_data = response.get("data")

        stories = response_data["data"]["items"]

        return status_code, stories


def user_profile_picture_upload_location(instance, filename):
    return f"instagram/user/{instance.username}/profile-picture/{filename}"


def user_stories_upload_location(instance, filename):
    return f"instagram/user/{instance.user.username}/stories/{filename}"
