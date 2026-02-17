import json
import logging
from datetime import timedelta

import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import BroadcastLog, BroadcastMessage, DownloadedTweet, ExternalLink, Settings, TelegramUser

logger = logging.getLogger(__name__)


@shared_task
def delete_old_data():
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)
    DownloadedTweet.objects.order_by("-created_at").filter(created_at__lt=one_month_ago).delete()


@shared_task
def broadcast_message_to_all_users(broadcast_id: str):
    """
    Main task to broadcast message to all active telegram users.
    Spawns individual tasks for each user with rate limiting.
    """
    try:
        _ = BroadcastMessage.objects.get(uuid=broadcast_id)
    except BroadcastMessage.DoesNotExist:
        return f"Broadcast {broadcast_id} not found"

    # Get all active and non-banned users
    active_users = TelegramUser.objects.filter(
        is_active=True,
        is_banned=False,
    ).values_list("user_id", flat=True)

    # Spawn individual tasks for each user
    for telegram_user_id in active_users:
        send_broadcast_to_user.delay(broadcast_id, telegram_user_id)

    return f"Spawned {len(active_users)} broadcast tasks"


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
    rate_limit="30/s",  # Telegram API limit: 30 messages per second
)
def send_broadcast_to_user(broadcast_id: str, telegram_user_id: str):
    """
    Send broadcast message to individual telegram user.
    This task has retry logic and rate limiting for Telegram API.
    """
    try:
        broadcast = BroadcastMessage.objects.get(uuid=broadcast_id)
        telegram_user = TelegramUser.objects.get(user_id=telegram_user_id)
    except (BroadcastMessage.DoesNotExist, TelegramUser.DoesNotExist) as e:
        return f"Error: {str(e)}"

    # Skip if already sent to this user
    if BroadcastLog.objects.filter(
        broadcast=broadcast,
        telegram_user=telegram_user,
    ).exists():
        return f"Already sent to user {telegram_user_id}"

    # Try to send message
    try:
        success = telegram_user.send_message(broadcast.message)

        if success:
            # Create success log
            BroadcastLog.objects.create(
                broadcast=broadcast,
                telegram_user=telegram_user,
                status=BroadcastLog.LogStatus.SUCCESS,
            )

            # Increment sent count atomically
            BroadcastMessage.objects.filter(uuid=broadcast_id).update(sent_count=F("sent_count") + 1)

            # Check completion
            _check_broadcast_completion(broadcast_id)

            return f"Successfully sent to {telegram_user_id}"
        else:
            raise Exception("Failed to send message (API returned False)")

    except Exception as e:
        error_message = str(e)

        # Create failure log
        BroadcastLog.objects.create(
            broadcast=broadcast,
            telegram_user=telegram_user,
            status=BroadcastLog.LogStatus.FAILED,
            error_message=error_message,
        )

        # Increment failed count atomically
        BroadcastMessage.objects.filter(uuid=broadcast_id).update(failed_count=F("failed_count") + 1)

        # Check completion
        _check_broadcast_completion(broadcast_id)

        return f"Failed to send to {telegram_user_id}: {error_message}"


@shared_task(
    autoretry_for=(Exception,),
    max_retries=3,
    retry_backoff=True,
)
def forward_tweet_to_channel(downloaded_tweet_id: str):
    """Forward a downloaded tweet's video to a Telegram channel."""
    config = Settings.get_solo()
    if not config.is_forward_to_channel or not config.forward_channel_id:
        return "Forwarding to channel is disabled"

    try:
        tweet = DownloadedTweet.objects.get(uuid=downloaded_tweet_id)
    except DownloadedTweet.DoesNotExist:
        return f"DownloadedTweet {downloaded_tweet_id} not found"

    tweet_data = tweet.tweet_data
    videos = tweet_data.get("videos", [])
    if not videos:
        return "No videos found in tweet data"

    bot_token = settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN
    headers = {"Content-Type": "application/json"}

    # Build inline keyboard with video quality links
    external_links = ExternalLink.objects.filter(is_active=True).order_by("-updated_at")
    external_link_buttons = [
        [{"text": link.title, "web_app": {"url": link.url}}]
        if link.is_web_app
        else [{"text": link.title, "url": link.url}]
        for link in external_links
    ]

    inline_keyboard = [
        [{"text": f"\U0001f517 {video['quality']}", "url": video["url"]} for video in videos[:3]],
    ] + external_link_buttons

    # Try sendPaidMedia first (same as user-facing send_video)
    url = f"https://api.telegram.org/bot{bot_token}/sendPaidMedia"
    payload = json.dumps(
        {
            "chat_id": config.forward_channel_id,
            "star_count": 1,
            "media": [{"type": "video", "media": videos[0]["url"]}],
            "caption": tweet_data.get("description", ""),
            "parse_mode": "HTML",
            "disable_notification": True,
            "reply_markup": {"inline_keyboard": inline_keyboard},
        }
    )
    response = requests.post(url, headers=headers, data=payload)

    if response.ok:
        return f"Forwarded tweet {downloaded_tweet_id} to channel"

    # Fallback to sendPhoto with thumbnail + inline keyboard
    thumbnail = tweet_data.get("thumbnail")
    if thumbnail:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        payload = json.dumps(
            {
                "chat_id": config.forward_channel_id,
                "photo": thumbnail,
                "parse_mode": "HTML",
                "disable_notification": True,
                "has_spoiler": tweet_data.get("is_nsfw", False),
                "reply_markup": {"inline_keyboard": inline_keyboard},
            }
        )
        response = requests.post(url, headers=headers, data=payload)

        if response.ok:
            return f"Forwarded tweet {downloaded_tweet_id} to channel (as photo)"

    logger.error("Failed to forward tweet %s to channel: %s", downloaded_tweet_id, response.text)
    raise Exception(f"Failed to forward tweet to channel: {response.text}")


def _check_broadcast_completion(broadcast_id: str):
    """
    Check if broadcast is completed and update status.
    Uses select_for_update to prevent race conditions.
    """
    with transaction.atomic():
        broadcast = BroadcastMessage.objects.select_for_update().get(uuid=broadcast_id)

        total_processed = broadcast.sent_count + broadcast.failed_count

        # Mark as completed if all messages processed
        if total_processed >= broadcast.total_users and broadcast.status == BroadcastMessage.BroadcastStatus.SENDING:
            broadcast.status = BroadcastMessage.BroadcastStatus.COMPLETED
            broadcast.completed_at = timezone.now()
            broadcast.save(update_fields=["status", "completed_at"])
