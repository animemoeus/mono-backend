from celery import shared_task

from .models import TiktokMonitor
from .utils import TiktokVideoNoWatermark


@shared_task(autoretry_for=(Exception,), max_retries=25, retry_backoff=True, soft_time_limit=3600)
def get_user_feed(tiktok_username: str) -> None:
    tiktok_user = TiktokVideoNoWatermark(tiktok_username)
    tiktok_user.save_videos()


@shared_task()
def tiktok_user_monitor():
    tiktok_users = TiktokMonitor.objects.filter(enabled=True).order_by("-updated_at")

    for user in tiktok_users:
        get_user_feed.delay(user.username)
