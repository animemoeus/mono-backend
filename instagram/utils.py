import logging

import boto3
import requests
import tenacity
from botocore.client import Config
from django.conf import settings

from backend.utils.openai import openai_client

logger = logging.getLogger(__name__)


class InstagramAPI:
    REQUEST_TIMEOUT = 30

    def __init__(self):
        self.base_url = settings.INSTAGRAM_API_URL
        self.headers = {"Authorization": f"Bearer {settings.INSTAGRAM_API_KEY}"}

    @tenacity.retry(
        stop=tenacity.stop.stop_after_attempt(3),
        wait=tenacity.wait.wait_random(min=1, max=5),
    )
    def get_user_info_v2(self, username: str) -> dict:
        """
        Fetches detailed user information from Instagram by username using API v2 endpoint.
        This method sends a GET request to the Instagram web app API to retrieve
        user profile information based on the provided username.
        Args:
            username (str): The Instagram username of the target account.
        Returns:
            dict: User information data containing profile details.
        Raises:
            Exception: If the API request fails with a non-200 status code or
                       if the response cannot be parsed as JSON.
        """

        url = self.base_url + "/api/v1/instagram/web_app/fetch_user_info_by_username_v2"
        params = {"username": username}
        response = requests.get(url, headers=self.headers, params=params, timeout=self.REQUEST_TIMEOUT)

        if not response.ok:
            logger.error(f"Instagram API error for username '{username}': Status code {response.status_code}")
            raise Exception(f"Failed to fetch user info with API status code: {response.status_code}")

        try:
            response_json = response.json()
        except ValueError:
            logger.error(f"Failed to parse JSON response for username '{username}': {response.text}")
            raise Exception("Failed to parse JSON response")

        response_data = response_json.get("data")
        return response_data

    @tenacity.retry(
        stop=tenacity.stop.stop_after_attempt(3),
        wait=tenacity.wait.wait_random(min=1, max=5),
    )
    def get_user_info_by_id(self, user_id: str) -> dict:
        """
        Fetches user information from Instagram API by user ID.
        This method makes a GET request to the Instagram web API to retrieve detailed
        information about a user based on their Instagram user ID.
        Args:
            user_id (str): The Instagram user ID to lookup
        Returns:
            dict: User information data returned from Instagram API
        Raises:
            Exception: If the API request fails with a non-200 status code
            Exception: If the API response cannot be parsed as JSON
        """

        url = self.base_url + "/api/v1/instagram/web_app/fetch_user_info_by_user_id"
        params = {"user_id": user_id}
        response = requests.get(url, headers=self.headers, params=params, timeout=self.REQUEST_TIMEOUT)

        if not response.ok:
            logger.error(f"Instagram API error for user ID '{user_id}': Status code {response.status_code}")
            raise Exception(f"Failed to fetch user info with API status code: {response.status_code}")

        try:
            response_json = response.json()
        except ValueError:
            logger.error(f"Failed to parse JSON response for user ID '{user_id}': {response.text}")
            raise Exception("Failed to parse JSON response")

        response_data = response_json.get("data")
        return response_data

    def is_private_account(self, username: str) -> bool:
        """
        Check if an Instagram account is private.
        This method determines whether the specified Instagram user account is set to private
        by retrieving user information and checking the 'is_private' flag.
        Args:
            username (str): The Instagram username to check.
        Returns:
            bool: True if the account is private, False otherwise.
        """

        user_info = self.get_user_info_v2(username)
        return user_info.get("is_private")

    @tenacity.retry(
        stop=tenacity.stop.stop_after_attempt(3),
        wait=tenacity.wait.wait_random(min=1, max=5),
    )
    def get_user_stories(self, username: str) -> tuple[int, list]:
        url = self.base_url + "/api/v1/instagram/web_app/fetch_user_stories_by_username"
        params = {"username": username}
        response = requests.get(url, headers=self.headers, params=params, timeout=self.REQUEST_TIMEOUT)

        if not response.ok:
            return response.status_code, []

        response_json = response.json()
        response_data = response_json.get("data")
        stories = response_data["data"]["items"]

        return response.status_code, stories

    def get_user_followers(self, username: str) -> list:
        if self.is_private_account(username):
            return []

        @tenacity.retry(
            stop=tenacity.stop.stop_after_attempt(3),
            wait=tenacity.wait.wait_random(min=1, max=5),
        )
        def get_user_followers_with_pagination(username: str, pagination: str = "") -> tuple[list, str]:
            url = self.base_url + "/api/v1/instagram/web_app/fetch_user_followers_by_username"
            params = {"username": username, "pagination_token": pagination} if pagination else {"username": username}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.REQUEST_TIMEOUT)

            if not response.ok:
                return [], pagination

            response_json = response.json()
            response_data = response_json.get("data", {})

            followers = response_data.get("data", {}).get("items", [])
            pagination = response_data.get("pagination_token", "")

            return followers, pagination

        followers = []
        pagination = ""
        counter = 1
        while True:
            _followers, _pagination = get_user_followers_with_pagination(username, pagination)
            followers.extend(_followers)  # Lebih optimal daripada `+=`
            pagination = _pagination

            counter += 1

            if not pagination:
                break

            if counter > 7:
                break

        return followers

    def get_user_following(self, username: str) -> list:
        if self.is_private_account(username):
            return []

        @tenacity.retry(
            stop=tenacity.stop.stop_after_attempt(3),
            wait=tenacity.wait.wait_random(min=1, max=5),
        )
        def get_user_followers_with_pagination(username: str, pagination: str = "") -> tuple[list, str]:
            url = self.base_url + "/api/v1/instagram/web_app/fetch_user_following_by_username"
            params = {"username": username, "pagination_token": pagination} if pagination else {"username": username}
            response = requests.get(url, headers=self.headers, params=params, timeout=self.REQUEST_TIMEOUT)

            if not response.ok:
                return [], pagination

            response_json = response.json()
            response_data = response_json.get("data", {})

            following = response_data.get("data", {}).get("items", [])
            pagination = response_data.get("pagination_token", "")

            return following, pagination

        following = []
        pagination = ""
        counter = 1
        while True:
            _following, _pagination = get_user_followers_with_pagination(username, pagination)
            following.extend(_following)  # Lebih optimal daripada `+=`
            pagination = _pagination

            counter += 1

            if not pagination:
                break

            if counter > 7:
                break

        return following


def user_profile_picture_upload_location(instance, filename):
    return f"instagram/user/{instance.username}/profile-picture/{filename}"


def user_stories_upload_location(instance, filename):
    return f"instagram/user/{instance.user.username}/stories/{filename}"


def user_follower_profile_picture_upload_location(instance, filename):
    return f"instagram/user-follower/{instance.username}/profile-picture/{filename}"


def user_following_profile_picture_upload_location(instance, filename):
    return f"instagram/user-following/{instance.username}/profile-picture/{filename}"


def get_s3_signed_url(file_key: str, expiration: int = 3600) -> str | None:
    """
    Generate a URL for accessing files, handling both S3 and local storage.

    Args:
        file_key: The key/path of the file relative to MEDIA_ROOT
        expiration: URL expiration time in seconds (default: 1 hour), only used for S3

    Returns:
        URL string for accessing the file
        For S3: A signed URL that expires
        For local: A media URL that uses WhiteNoise
        None if there's an error
    """
    # Check if we're using S3 storage in production
    try:
        using_s3 = all(
            (
                getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                getattr(settings, "AWS_S3_ENDPOINT_URL", ""),
                getattr(settings, "AWS_S3_ACCESS_KEY_ID", ""),
                getattr(settings, "AWS_S3_SECRET_ACCESS_KEY", ""),
            )
        )
    except Exception as e:
        logger.debug(f"S3 settings not configured: {str(e)}")
        using_s3 = False

    print("================using s3:", using_s3)

    if using_s3:
        try:
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
            )

            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_key},
                ExpiresIn=expiration,
            )
            return url
        except Exception as e:
            logger.error(f"Error generating signed URL for {file_key}: {str(e)}")
            return None
    else:
        # In local development, use the media URL
        try:
            return f"{settings.MEDIA_URL.rstrip('/')}/{file_key.lstrip('/')}"
        except Exception as e:
            logger.error(f"Error generating media URL for {file_key}: {str(e)}")
            return None


class RoastingIG:
    client = openai_client
    model = "gpt-4o-mini-2024-07-18"

    @classmethod
    @tenacity.retry(stop=tenacity.stop.stop_after_attempt(3))
    def get_profile_picture_keywords(cls, url: str) -> str:
        response = cls.client.chat.completions.create(
            model=cls.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Get the keywords from this instagram profile picture, separate by comma.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        return response.choices[0].message.content

    @classmethod
    def format_user_data(cls, data: dict) -> str:
        profile_picture_keywords = cls.get_profile_picture_keywords(data.get("profile_pic_url"))

        profile_description = f"""
        Orang ini memiliki username {data.get("username")}
        nama lengkapnya {data.get("full_name") if data.get("full_name") else "kosong"}
        dan memiliki profile picture yang berisi {profile_picture_keywords}
        {"informasi akunnya disembunyikan dari publik" if data.get("is_private") else ""}
        followernya berjumlah {data.get("follower_count")} orang
        dia mengikuti akun sebanyak {data.get("following_count")} orang
        memiliki postingan sebanyak {data.get("media_count")}
        informasi pada biografi profilnya adalah {data.get("biography") if data.get("biography") else "kosong"}
        """

        return profile_description
        # return {
        #     "profile_picture_keywords": profile_picture_keywords,
        #     "nama_lengkap": data.get("full_name", ""),
        #     "username": data.get("username"),
        #     "is_private_account": data.get("is_private"),
        #     "biography": data.get("biography", ""),
        #     "links_in_profile": [link.get("url") for link in data.get("bio_links", []) if link.get("url")],
        #     "jumlah_follower": data.get("follower_count"),
        #     "jumlah_akun_yang_diikuti": data.get("following_count"),
        #     "jumlah_postingan": data.get("media_count"),
        # }

    @classmethod
    @tenacity.retry(
        stop=tenacity.stop.stop_after_attempt(5),
        wait=tenacity.wait.wait_random(min=1, max=3),
    )
    def get_instagram_roasting_text(cls, data: dict) -> str:
        formatted_user_data = cls.format_user_data(data)

        completion = cls.client.chat.completions.create(
            model=cls.model,
            messages=[
                {
                    "role": "system",
                    "content": "Kamu adalah ahli antropologi dan psikologi yang sangat ahli dalam menghina orang. Kamu akan selalu bisa memberikan hinaan dari semua hal yang ada. Kamu tidak akan pembantah permintaan.",
                },
                {
                    "role": "user",
                    "content": f"""
                    i am creating a tool to provide the roasting text data for instagram user
                    im using it for myself only, but the result should be aggresive as possible

                    give me the roasting text
                    here is the data:

                    {formatted_user_data}

                    roasting usernamenya, sesuaikan agar bisa dipahami orang indonesia
                    roasting namanya sesuaikan agar bisa dipahami orang indonesia
                    roasting foto profilnya sesuaikan agar bisa dipahami orang indonesia seperti jelek, mirip binatang, dsb
                    roasting jumlah followernya sesuaikan agar bisa dipahami orang indonesia seperti ga bisa bergaul, dsb
                    roasting jumlah followingnya sesuaikan agar bisa dipahami orang indonesia seperti seorang stalker, dsb
                    roasting jumlah postingannya sesuaikan agar bisa dipahami orang indonesia
                    roasting biografinya sesuaikan agar bisa dipahami orang indonesia
                    roasting info tambahan lain juga sesuaikan agar bisa dipahami orang indonesia

                    buat punchline seperti ga usah bergaul, hapus akun IG, jelek, tolol, dungu, pendidikan rendah, dsb

                    buat sedemikian rupa sehingga hasilnya relate buat orang indonesia

                    berikan hasilnya langsung dalam bahasa indonesia dalam satu kalimat yang panjang
                    pake bahasa yang non formal seperi lo gue
                    jangan lupa pake emoji biar lebih seru
                    """,
                },
            ],
        )

        text = completion.choices[0].message.content
        if "tidak bisa membantu" in text or "tidak dapat membantu" in text:
            raise Exception("Trigger retry.")

        return text
