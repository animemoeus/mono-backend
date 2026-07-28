import requests
from django.conf import settings
from django.core.cache import cache
from requests import Response
from saiyaku import retry

from .models import SavedTiktokVideo


class TikHubAPI:
    def get_user_id(self, username: str) -> str:
        # Check if the user id is already in the cache
        if cache.get(f"tiktok_user_id_{username}"):
            return cache.get(f"tiktok_user_id_{username}")

        response = self.request(f"/api/v1/tiktok/web/fetch_user_profile?uniqueId={username}")

        if not response.ok:
            raise Exception(f"{self.__class__.__name__}: Request failed with status code {response.status_code}.")

        response_data = response.json().get("data")
        user_info = response_data.get("userInfo")

        if not user_info:
            raise Exception(f"{self.__class__.__name__}: There is no user with username {username}.")

        user = user_info.get("user")
        user_id = user.get("secUid")

        # Cache the user id for 1 year
        cache.set(f"tiktok_user_id_{username}", user_id, timeout=31536000)

        return user_id

    def get_user_info(self, username: str):
        user_id = self.get_user_id(username)
        response = self.request(f"/api/v1/tiktok/app/v3/handler_user_profile?sec_user_id={user_id}")

        response_data = response.json().get("data")
        raw_user_info = response_data.get("user")

        user_info = {
            "nickname": raw_user_info.get("nickname", ""),
            "username": raw_user_info.get("unique_id"),
            "user_id": user_id,
            "avatar": (
                raw_user_info.get("avatar_larger")["url_list"][-1]
                if raw_user_info.get("avatar_larger") and raw_user_info.get("avatar_larger")["url_list"]
                else ""
            ),
            "followers": raw_user_info.get("follower_count"),
            "following": raw_user_info.get("following_count"),
            "visible_content_count": raw_user_info.get("visible_videos_count"),
        }

        return user_info

    @staticmethod
    def request(url: str, method: str = "GET") -> Response:
        """
        Makes a request to the specified URL with the given method.

        :param url: The endpoint to send the request to.
        :param method: The HTTP method to use for the request. Defaults to "GET".
        :return: The response object from the request.
        """

        base_url = settings.TIKHUB_API_URL
        headers = {"Authorization": f"Bearer {settings.TIKHUB_API_KEY}"}

        response = requests.request(method, f"{base_url}/{url}", headers=headers, timeout=10)
        return response


class TiktokVideoNoWatermark:
    """https://github.com/yi005/Tiktok-Video-No-Watermark"""

    def __init__(self, username: str) -> None:
        self.username = username

    def __str__(self):
        return self.username

    @property
    def posts(self) -> list[dict]:
        # Because of the API limitations, we only get the first page of the feed data.
        # TODO: Use the cursor data to get more information
        url = f"https://www.tikwm.com/api/user/posts?unique_id={self.username}&count=33"
        response = requests.request("GET", url)

        tiktok_videos = response.json().get("data").get("videos")
        return tiktok_videos

    @retry(tries=10, delay=10)
    def get_post_data_once(self):
        url = f"https://www.tikwm.com/api/user/posts?unique_id={self.username}&count=50"
        response = requests.request("GET", url)

        data = response.json().get("data")
        return data

    @retry(tries=10, delay=10)
    def get_post_data_with_cursor(self, cursor=0):
        url = f"https://www.tikwm.com/api/user/posts?unique_id={self.username}&count=50&cursor={cursor}"
        response = requests.request("GET", url)

        data = response.json().get("data")
        return data

    @retry(tries=10, delay=10)
    def get_all_post(self):
        data = self.get_post_data_once()
        cursor = data.get("cursor")
        has_more = data.get("hasMore")
        videos = data.get("videos")

        while has_more:
            data = self.get_post_data_with_cursor(cursor=cursor)
            cursor = data.get("cursor")
            has_more = data.get("hasMore")
            videos += data.get("videos")

            if not has_more:
                break

        return videos[::-1]

    def save_videos(self):
        # Only send video that not sent yet
        for video in self.get_all_post():
            if not SavedTiktokVideo.objects.filter(id=video.get("video_id")).exists():
                SavedTiktokVideo.objects.create(id=video.get("video_id"))
                send_to_private_telegram_channel(video.get("play"), video.get("title"))


@retry(tries=10, delay=1)
def send_to_private_telegram_channel(video_url: str, caption: str = "") -> None:
    """Sent to private Telegram channel by via Telegram Bot"""

    url = f"https://api.telegram.org/bot{settings.TIKTOK_MONITOR_TELEGRAM_BOT_SECRET}/sendDocument"
    payload = {
        "chat_id": settings.TIKTOK_MONITOR_TELEGRAM_PRIVATE_CHANNEL_ID,
        "document": video_url,
        "caption": caption,
        "disable_notification": True,
    }

    response = requests.request("POST", url, data=payload)
    return response.status_code
