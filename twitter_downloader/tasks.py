from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import BroadcastLog, BroadcastMessage, DownloadedTweet, TelegramUser


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
