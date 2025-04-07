import re

import requests
from django.conf import settings
from saiyaku import retry


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
            raise TooManyRequestException(
                "Woah, too many requests! Maybe take a little break? I'll keep trying... 🔄😜"
            )

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
    def __init__(self, tweet_url: str):
        self.tweet_url = tweet_url

    def get_tweet_id(self) -> str:
        """
        Extract the tweet ID from a Twitter/X URL.

        Returns:
        str: The tweet ID extracted from the URL.

        Example:
        URL: https://twitter.com/username/status/1274296339375853568
        Returns: 1274296339375853568
        """
        # Support both twitter.com and x.com
        pattern = r"(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/(?:#!\/)?[^/]+/status(?:es)?/(\d+)"
        match = re.search(pattern, self.tweet_url)

        print(match)

        if not match:
            raise ValueError("Invalid Twitter/X URL format")

        tweet_id = match.group(1)
        return tweet_id


def get_tweet_url(text: str) -> str:
    urls = re.findall(r"https://\S+", text.lower())
    url = urls[0] if urls else ""

    return url
