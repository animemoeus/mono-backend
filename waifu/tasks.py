import random

import pyscord_storage
from celery import shared_task

from .models import DiscordWebhook, Image


@shared_task()
def send_waifu():
    from waifu.utils import refresh_expired_urls

    webhooks = DiscordWebhook.objects.filter(is_enabled=True)

    # get random waifu from database
    total_records = Image.objects.count()
    random_index = random.randint(0, total_records - 1)
    waifu = Image.objects.order_by("id")[random_index]

    new_url = waifu.original_image
    if "tumblr.com" not in waifu.original_image:
        new_urls = refresh_expired_urls([waifu.original_image])
        new_url = new_urls.get(waifu.original_image)

    for webhook in webhooks:
        webhook.send_image(
            new_url,
            waifu.is_nsfw,
            waifu.creator_name,
        )


@shared_task()
def save_pixiv_illust(illust_data: dict, pyscord_data: dict) -> None:
    Image.objects.create(
        image_id=pyscord_data.get("id"),
        original_image=pyscord_data.get("url"),
        thumbnail=pyscord_data.get("proxy_url"),
        width=pyscord_data.get("width"),
        height=pyscord_data.get("height"),
        creator_name=illust_data.get("creator_name"),
        creator_username=illust_data.get("creator_username"),
        caption=illust_data.get("title"),
        source=illust_data.get("source"),
    )


@shared_task(autoretry_for=(Exception,), max_retries=10, retry_backoff=True)
def send_pixiv_image_url_to_pyscord_storage(illust_data: dict, image_url: str) -> None:
    """Change original Pixiv image url to Discord image url"""

    response = pyscord_storage.upload_from_url("animemoeus-waifu.jpg", image_url)
    if response.get("status") != 200:
        raise Exception(response)

    pyscord_data = response.get("data")
    save_pixiv_illust(illust_data, pyscord_data)


@shared_task()
def update_pixiv_image_url_and_save_to_db(illust_data: dict) -> None:
    for image in illust_data.get("images"):
        send_pixiv_image_url_to_pyscord_storage.delay(illust_data, image)
