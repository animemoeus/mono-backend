import logging
import re

import requests
import tenacity
from django.conf import settings
from saiyaku import retry
from tenacity import stop_after_attempt, stop_after_delay

logger = logging.getLogger(__name__)


class TooManyRequestException(Exception):
    pass


class TwitterDownloader:
    URL = settings.TWITTER_DOWNLOADER_API_URL
    HEADERS = {
        "X-RapidAPI-Key": settings.TWITTER_DOWNLOADER_KEY,
        "X-RapidAPI-Host": settings.TWITTER_DOWNLOADER_HOST,
    }
    COOKIE = settings.TWITTER_DOWNLOADER_COOKIE

    def __init__(self, url, headers):
        self.URL = url
        self.HEADERS = headers

    @classmethod
    @retry(exceptions=TooManyRequestException, delay=1, tries=5)
    def get_video_data(cls, tweet_url: str):
        querystring = {
            "url": tweet_url,
            "Cookie": cls.COOKIE,
        }

        response = requests.get(cls.URL, headers=cls.HEADERS, params=querystring)

        # Raise too many request exception to trigger auto retry
        if response.status_code == 429:
            raise TooManyRequestException

        try:
            response = response.json()
        except ValueError:
            return None

        if not response.get("data"):
            return None

        if response.get("data") and response.get("data")[0].get("type") != "video":
            return None

        _videos = []
        for data in response.get("data")[0].get("video_info"):
            if data.get("bitrate"):
                _videos.append(
                    {
                        "bitrate": data.get("bitrate"),
                        "size": re.findall(r"[0-9]+x[0-9]+", data.get("url"))[0],
                        "url": data.get("url"),
                    }
                )

        _videos = sorted(_videos, key=lambda d: d["bitrate"])[::-1]

        return {
            "id": response.get("id"),
            "thumbnail": response.get("data")[0].get("media"),
            "description": response.get("description") or "",
            "videos": _videos,
        }

    @staticmethod
    def extract_tweet_id_from_url(tweet_url: str) -> str:
        """
        Extract the tweet ID from a Twitter/X URL.

        Args:
            tweet_url (str): Full Twitter URL

        Returns:
            str: The extracted tweet ID
        """
        import re

        match = re.search(r"/status/(\d+)", tweet_url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Twitter URL format")


class TwitterDownloaderAPIV2:
    """
    A class for fetching Twitter/X data using a provided API.

    Attributes:
        URL (str): The base URL for the Twitter downloader API.
        COOKIE (str): The cookie string for authentication.
        HEADERS (dict): Headers for the API request including authentication keys.
        tweet_url (str): The URL of the tweet to fetch data for.
        tweet_data (dict): The fetched data of the tweet.
    """

    URL = settings.TWITTER_DOWNLOADER_API_URL
    COOKIE = settings.TWITTER_DOWNLOADER_COOKIE
    HEADERS = {
        "X-RapidAPI-Key": settings.TWITTER_DOWNLOADER_KEY,
        "X-RapidAPI-Host": settings.TWITTER_DOWNLOADER_HOST,
    }

    def __init__(self, tweet_url: str):
        """
        Initialize the TwitterDownloaderAPIV2 instance.

        Args:
            tweet_url (str): The URL of the tweet to fetch data for.
        """

        self.tweet_url = tweet_url
        self.tweet_data = self._get_tweet_data()
        self.id = self.tweet_data.get("id")
        self.created_at = self.tweet_data.get("created_at")
        self.description = self.tweet_data.get("description")
        self.data = self.tweet_data.get("data")

    @retry(exceptions=TooManyRequestException, delay=1, tries=7)
    def _get_tweet_data(self) -> dict:
        """
        Fetch tweet data from the Twitter downloader API.

        Returns:
            dict: The response data containing tweet information.

        Raises:
            TooManyRequestException: If too many requests are made in a short time.
            Exception: If the response is not JSON or if data is missing.
        """

        querystring = {
            "url": self.tweet_url,
            "Cookie": self.COOKIE,
        }

        response = requests.get(self.URL, headers=self.HEADERS, params=querystring, timeout=5)

        # Handle rate-limiting error
        if response.status_code == 429:
            raise TooManyRequestException("Woah, too many requests! Maybe take a little break? I'll keep trying... 🔄😜")

        # Attempt to parse JSON response
        try:
            response_data = response.json()
        except ValueError:
            raise Exception("Hmm, the response doesn't look right. Are you sure it's JSON? 🧐🛑")

        # Check if the required data is in the response
        if not response_data.get("data"):
            raise Exception(
                "Looks like I can't find that tweet... Are you sure it's still there? Or maybe it's deleted? 🤷‍♀️🚫"
            )

        return response_data


class TwitterDownloaderAPIV3:
    """
    Twitter API client for fetching tweet details using v3 API.

    This class handles API authentication, request formatting, response validation,
    and data extraction for Twitter/X tweet content including text, photos, and videos.

    Attributes:
        API_URL (str): Base URL for the Twitter API.
        AUTHORIZATION (dict): Authorization headers with Bearer token.
    """

    API_URL = settings.TWITTER_DOWNLOADER_API_URL
    AUTHORIZATION = {
        "Authorization": f"Bearer {settings.TWITTER_DOWNLOADER_API_KEY}",
    }

    def __init__(self):
        pass

    @tenacity.retry(
        stop=(stop_after_delay(10) | stop_after_attempt(3)),
    )
    def get_tweet_data(self, tweet_id: str) -> dict:
        """
        Fetch and process data for a specific tweet.

        Args:
            tweet_id (str): The Twitter/X tweet ID to retrieve.

        Returns:
            dict: Processed tweet data including:
                - tweet_id: The ID of the tweet
                - text: The text content of the tweet
                - photos: List of photo URLs
                - videos: List of video objects with variants
                - is_nsfw: Boolean indicating if content is sensitive

        Raises:
            Exception: If the API request fails, response validation fails,
                      or network connectivity issues occur.
        """
        logger.debug(f"Fetching tweet data for ID: {tweet_id}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self.AUTHORIZATION,
        }
        base_url = self.API_URL.rstrip("/")  # Remove trailing slash if exists
        path = "/".join(["api", "v1", "twitter", "web", "fetch_tweet_detail"])
        url = f"{base_url}/{path}"

        try:
            self.response = requests.get(
                url,
                headers=headers,
                timeout=30,
                params={"tweet_id": tweet_id},
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when connecting to Twitter API: {str(e)}")

        response_data = self.get_response_data()

        entities = response_data.get("entities", {})

        tweet_data = {}
        tweet_data_photos = []
        tweet_data_videos = []

        media_list = entities.get("media", [])
        for media in media_list:
            # For each media, the type is should be "photo", "video", or "animated_gif"
            if media.get("type") == "photo":
                tweet_data_photos.append(media.get("media_url_https"))

            # Twitter API v3 returns videos and gifs as "video" or "animated_gif"
            # The gif is not have width and height
            if media.get("type") == "video" or media.get("type") == "animated_gif":
                video_info = media.get("video_info", {})

                if video_info:
                    video_variants = video_info.get("variants", [])
                    tweet_video_variants = []  # Separate list for variants of current video

                    for variant in video_variants:
                        if variant.get("content_type") == "video/mp4":
                            tweet_video_variants.append(
                                {
                                    "url": variant.get("url"),
                                    "thumbnail": media.get("media_url_https"),
                                    "bitrate": variant.get("bitrate"),
                                    "size": re.findall(r"[0-9]+x[0-9]+", variant.get("url"))[0]
                                    if re.findall(r"[0-9]+x[0-9]+", variant.get("url"))
                                    else "0x0",  # Default to "0x0" if no size found (e.g., gif variant does not have size)
                                }
                            )

                    # Sort variants by bitrate in descending order
                    tweet_video_variants = sorted(tweet_video_variants, key=lambda d: d["bitrate"])[::-1]

                    # Add the video with all its variants as a separate entry
                    if tweet_video_variants:
                        tweet_data_videos.append(
                            {
                                "media_id": media.get("id_str", ""),
                                "type": media.get("type", "video"),
                                "thumbnail": media.get("media_url_https"),
                                "variants": tweet_video_variants,
                            }
                        )

        tweet_data["tweet_id"] = response_data.get("id")
        tweet_data["text"] = response_data.get("text")
        tweet_data["photos"] = tweet_data_photos
        tweet_data["videos"] = tweet_data_videos
        tweet_data["is_nsfw"] = response_data.get("sensitive", False)
        # tweet_data["raw"] = response_data

        logger.info(f"Successfully retrieved data for tweet ID: {tweet_id}")
        return tweet_data

    def _validate_response_status(self) -> None:
        """
        Validates the HTTP response status from the Twitter API request.
        This private method checks if the response status is okay (2xx).
        If the response is not successful, it raises an exception with
        the status code information.
        Raises:
            Exception: If the response status is not okay (not 2xx),
                      includes the status code in the error message.
        Returns:
            None: If validation passes, returns nothing.
        """

        if not self.response.ok:
            raise Exception(f"Failed to fetch tweet data from API. Status code: {self.response.status_code}")

    def _validate_response_json(self) -> None:
        """
        Validates the JSON response from the Twitter API request.
        This private method checks if the response is in JSON format.
        If the response is not JSON, it raises an exception.
        Raises:
            Exception: If the response is not JSON.
        Returns:
            None: If validation passes, returns nothing.
        """
        try:
            self.response.json()
        except ValueError:
            raise Exception("Failed to parse API response to JSON. Please check the response format.")

    def _validate_response_data(self) -> None:
        """
        Validates the data in the JSON response from the Twitter API request.
        This private method checks if the response contains the expected data.
        If the data is missing or not in the expected format, it raises an exception.
        Raises:
            Exception: If the response data is missing or not in the expected format.
        Returns:
            None: If validation passes, returns nothing.
        """
        response_data = self.response.json()
        if not response_data.get("data"):
            raise Exception("Unable to find the tweet data in the API response. Please check the response structure.")

    def get_response_data(self) -> dict:
        """
        Returns the response data from the Twitter API request.
        This method checks if the response is valid and contains the expected data.
        If the data is not available, it raises an exception.
        Returns:
            dict: The response data from the Twitter API request.
        Raises:
            Exception: If the response data is not available or not in the expected format.
        """

        self._validate_response_status()
        self._validate_response_json()
        self._validate_response_data()

        response_data = self.response.json()

        data = response_data.get("data")
        return data if data.get("created_at") else None


def get_tweet_url(text: str) -> str:
    urls = re.findall(r"https://\S+", text.lower())
    url = urls[0] if urls else ""

    return url


def get_tweet_id_from_url(tweet_url: str) -> str:
    """
    Extract the tweet ID from a Twitter/X URL.

    Args:
        tweet_url (str): Full Twitter URL

    Returns:
        str: The extracted tweet ID
    """
    match = re.search(r"/status/(\d+)", tweet_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Twitter URL format")
