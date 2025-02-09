import json
from typing import Any

import requests
from django.conf import settings
from pixivpy3 import AppPixivAPI

from .tasks import update_pixiv_image_url_and_save_to_db


def refresh_expired_urls(urls: list[str]) -> dict:
    """
    Refresh expired Discord attachment URLs using the Discord API.

    This function takes a list of expired attachment URLs and sends a POST request
    to the Discord API to refresh them. The response contains a mapping of original
    URLs to their refreshed counterparts.

    Args:
        urls (list[str]): A list of expired URLs that need to be refreshed.

    Returns:
        dict: A dictionary mapping the original URLs to the refreshed URLs.

    Raises:
        Exception: If the API request to refresh URLs fails, an exception is raised
        with an error message.

    Example:
        urls = ["https://cdn.discordapp.com/attachments/123456", "https://cdn.discordapp.com/attachments/789012"]
        refreshed_urls = refresh_expired_urls(urls)
        # refreshed_urls will be a dictionary mapping original URLs to new ones.
    """

    api_url = settings.DISCORD_REFRESH_URL
    headers = {
        "Authorization": f"Bot {settings.WAIFU_DISCORD_REFRESH_URL_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"attachment_urls": urls})

    response = requests.request("POST", api_url, headers=headers, data=payload)
    if not response.ok:
        raise Exception("Oh no! Failed to refresh URLs. Discord API isn’t playing nice right now.")

    result = {
        data.get("original"): data.get("refreshed")
        for data in response.json().get("refreshed_urls")
        if data.get("refreshed")
    }
    return result


def refresh_serializer_data_urls(data: list[dict]) -> list[dict]:
    """
    Refresh expired URLs in the serializer data.

    Args:
        data (list[dict]): A list of dictionaries containing the serializer data.

    Returns:
        list[dict]: The updated list of dictionaries with refreshed URLs.
    """
    urls = []

    for item in data:
        if "cdn.discordapp.com" in item.get("original_image", ""):
            urls.append(item.get("original_image"))
        if "media.discordapp.net" in item.get("thumbnail", ""):
            urls.append(item.get("thumbnail"))

    if not urls:
        return data

    refreshed_urls = refresh_expired_urls(urls)

    for item in data:
        item["original_image"] = refreshed_urls.get(item.get("original_image"), item.get("original_image"))
        item["thumbnail"] = refreshed_urls.get(item.get("thumbnail"), item.get("thumbnail"))

    return data


class PixivIllust:
    IllustDetail = Any

    def __init__(self, illust_link: str) -> None:
        self.__illust_link = illust_link
        self.__api = AppPixivAPI()
        self.__api.auth(refresh_token=settings.PIXIVPY_3_REFRESH_TOKEN)

    @property
    def illust_detail(self) -> IllustDetail:
        """Return a dictionary that contains information about pixiv illustraion details"""

        illust_id = self.__illust_link.split("/")[-1]
        json_result = self.__api.illust_detail(illust_id)
        json_result = json_result.get("illust")

        # handle multiple images
        if json_result.get("meta_pages"):
            images = [image.get("image_urls").get("original") for image in json_result.get("meta_pages")]

        # handle single image
        if json_result.get("meta_single_page"):
            images = [
                json_result.get("meta_single_page").get("original_image_url"),
            ]

        formated_result = {
            "creator_name": json_result.get("user").get("name"),
            "creator_username": json_result.get("user").get("account"),
            "title": json_result.get("title"),
            "images": images,
            "source": self.__illust_link,
        }

        return formated_result

    def save(self) -> None:
        update_pixiv_image_url_and_save_to_db.delay(self.illust_detail)
