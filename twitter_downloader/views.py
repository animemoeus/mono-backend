import re

from django.shortcuts import render
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.utils.telegram import TelegramWebhookParser

from .models import DownloadedTweet
from .models import Settings as TwitterDownloaderSettings
from .models import TelegramUser
from .serializers import ValidateTelegramMiniAppDataSerializer
from .utils import TwitterDownloaderAPIV2, TwitterDownloaderAPIV3, get_tweet_id_from_url, get_tweet_url


class SafelinkView(View):
    # This decorator is used to allow the iframe to load the page (from Telegram app)
    @xframe_options_exempt
    def get(self, request):
        uuid = request.GET.get("key", None)

        return render(request, "twitter_downloader/download.html", context={"uuid": uuid})

    @csrf_exempt
    def post(self, request):
        uuid = request.POST.get("uuid")

        tweet = DownloadedTweet.objects.get(uuid=uuid)
        tweet_data = tweet.tweet_data

        videos = tweet_data.get("videos", [])
        for video in videos:
            tweet.telegram_user.send_video(
                {
                    "description": tweet_data.get("text", ""),
                    "videos": video.get("variants", []),
                    "thumbnail": video.get("thumbnail"),
                }
            )

        return render(request, "twitter_downloader/success.html")


class TelegramWebhookView(APIView):
    def post(self, request):
        # Fix DDOS Issue 438
        # https://github.com/animemoeus/backend/issues/438
        if (
            TwitterDownloaderSettings.get_solo().secret_token
            and request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            != TwitterDownloaderSettings.get_solo().secret_token
        ):
            return Response(
                {"message": "WTF?!"},  # TODO: Change this to a more appropriate message
                status=status.HTTP_401_UNAUTHORIZED,
            )

        webhook = TelegramWebhookParser(request.body)
        if not webhook.data:
            # Telegram webhook mechanism will try to retry sending the request if it fails
            # So we need to return 200 OK to avoid Telegram from retrying
            return Response(status=status.HTTP_200_OK)

        # Get or create TelegramUser
        user_data = webhook.data.get("user")
        telegram_user, _ = TelegramUser.objects.get_or_create(
            user_id=user_data.get("id"),
            defaults={
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name") or "",
                "username": user_data.get("username") or "",
            },
        )

        # Update TelegramUser data
        telegram_user.is_active = True
        telegram_user.first_name = user_data.get("first_name")
        telegram_user.last_name = user_data.get("last_name") or ""
        telegram_user.username = user_data.get("username") or ""
        telegram_user.request_count += 1
        telegram_user.save()

        # Check if the bot is under maintenance
        if self.is_maintenance:
            telegram_user.send_maintenance_message()
            return Response(status=status.HTTP_200_OK)

        # Check if the user is banned
        if telegram_user.is_banned:
            telegram_user.send_banned_message()
            return Response(status=status.HTTP_200_OK)

        text_message = webhook.data.get("text_message")
        print("text_message", text_message)
        if text_message:
            self.handle_text_message(telegram_user, text_message)

        return Response()

    @property
    def is_maintenance(self):
        """
        Check if the Twitter downloader is in maintenance mode.
        Returns:
            bool: True if the system is in maintenance mode, False otherwise.
        """

        return TwitterDownloaderSettings.get_solo().is_maintenance

    def handle_text_message(self, telegram_user: TelegramUser, message: str):
        # Handle /start command
        if message.lower().startswith("/start"):
            self.handle_start_command(telegram_user)

        # Handle /contact command
        elif message.lower().startswith("/contact"):
            self.handle_contact_command(telegram_user)

        # Handle /about command
        elif message.lower().startswith("/about"):
            self.handle_about_command(telegram_user)

        # Handle tweet link
        elif "https://x.com" in message.lower() or "https://twitter.com" in message.lower():
            telegram_user.send_chat_action("typing")
            self.handle_tweet_link(telegram_user, message)

        # Handle other messages
        else:
            self.handle_other_messages(telegram_user)

    def handle_start_command(self, telegram_user):
        telegram_user.send_message("Welcome to Twitter Video Downloader Bot!\n\no(*￣▽￣*)ブ")
        telegram_user.send_message("Send me a tweet link and I will send you the video and download link!")

    def handle_contact_command(self, telegram_user):
        telegram_user.send_message("Please contact me at arter@animemoe.us for any inquiries.")

    def handle_about_command(self, telegram_user):
        about_message = "This is the Twitter Video Downloader Bot.\n\n"
        about_message += "It allows you to download videos from Twitter by sending a tweet link.\n\n"
        about_message += "Developed by Arter Tendean.\n\n"
        about_message += "For more information, visit our website at https://animemoe.us"
        telegram_user.send_message(about_message)

    def handle_tweet_link(self, telegram_user, message):
        # Extract all strings starting with "https"
        urls = re.findall(r"https://\S+", message.lower())
        url = urls[0] if urls else None

        try:
            tweet_id = get_tweet_id_from_url(url)
        except Exception:
            telegram_user.send_message(
                "Hmm... I couldn't find a valid tweet URL in your message. Could you double-check it? 😊"
            )
            return Response(status=status.HTTP_200_OK)

        twitter_api = TwitterDownloaderAPIV3()

        try:
            tweet_data = twitter_api.get_tweet_data(tweet_id)
        except Exception:
            telegram_user.send_message("Sorry, I can't find any video in that tweet link.")
            return Response(status=status.HTTP_200_OK)

        if not tweet_data:
            telegram_user.send_message("Sorry, I can't find any video in that tweet link.")
            return Response()

        downloaded_tweet = DownloadedTweet.objects.create(
            tweet_url=message,
            telegram_user=telegram_user,
            tweet_data=tweet_data,
        )
        downloaded_tweet.send_to_telegram_user()

    def handle_other_messages(self, telegram_user):
        telegram_user.send_message(
            "Haha, I'm just a bot.\n\nI can't understand everything.\n\nTry sending a different command!"
        )


class TelegramWebhookV2View(APIView):
    def post(self, request):
        telegram_webhook = TelegramWebhookParser(request.body)

        try:
            webhook_user = telegram_webhook.get_user()
        except Exception as e:
            return self._response_with_message(
                f"Oops! There was an error: {str(e)}. Please try again.",
                status.HTTP_400_BAD_REQUEST,
            )

        # Get or create Telegram User
        telegram_user = self._get_or_create_telegram_user(webhook_user)
        telegram_user.request_count += 1
        telegram_user.save()

        # Check for maintenance mode and return immediately if true
        if self._is_maintenance_mode():
            telegram_user.send_maintenance_message()
            return self._response_with_message(
                "Sorry! We're currently undergoing maintenance. Please check back later! 😝"
            )

        # Check if user is banned and return immediately if true
        if telegram_user.is_banned:
            telegram_user.send_banned_message()
            return self._response_with_message(
                "Uh-oh! Your account has been banned. Please contact support for assistance. ☠️"
            )

        # Handle text message if present
        text_message = telegram_webhook.get_text_message()

        if text_message:
            self._handle_text_message(telegram_user, text_message)
            return self._response_with_message(f"Got it! You've sent a text message: {text_message}")
        else:
            telegram_user.send_message("Hmmm 🤔")

        return self._response_with_message("Hello from arter tendean! 😄")

    def _get_or_create_telegram_user(self, webhook_user) -> TelegramUser:
        # Helper method to get or create a Telegram user
        telegram_user, _ = TelegramUser.objects.get_or_create(
            user_id=webhook_user.get("id"),
            defaults={
                "first_name": webhook_user.get("first_name"),
                "last_name": webhook_user.get("last_name"),
                "username": webhook_user.get("username"),
                "is_active": True,
            },
        )
        return telegram_user

    def _is_maintenance_mode(self) -> bool:
        # Check if the system is in maintenance mode
        return TwitterDownloaderSettings.get_solo().is_maintenance

    def _handle_text_message(self, telegram_user: TelegramUser, message: str):
        if message.startswith("/start"):
            message = f"Hey <b>{telegram_user.first_name}</b>!\n\nWelcome to the <b>Twitter Video Downloader Bot</b>! 🎥📥\n\nI'm here to help you download videos from Twitter easily and quickly! 😄\n\n✨ Just send me a link to a Twitter video, and I’ll handle the rest! ✨"

            telegram_user.send_message(message)

        # Handle the text message that possibly contains tweet data
        elif "https://x.com" in message.lower() or "https://twitter.com" in message.lower():
            tweet_url = get_tweet_url(message.lower())
            if not tweet_url:
                telegram_user.send_message(
                    "Hmm... I couldn't find a valid tweet URL in your message. Could you double-check it? 😊"
                )

            try:
                twitter_downloader = TwitterDownloaderAPIV2(tweet_url=tweet_url)
            except Exception as e:
                telegram_user.send_message(str(e))
                return

            print(twitter_downloader)

        else:
            # Unknown text message
            telegram_user.send_message(
                "I'm not quite sure how to process that message. Can you try sending something different? 🤔"
            )

    def _response_with_message(self, message, status=status.HTTP_200_OK):
        # Helper method to create a Response with a message
        return Response({"message": message}, status=status)


class ValidateTelegramMiniAppDataView(GenericAPIView):
    serializer_class = ValidateTelegramMiniAppDataSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_200_OK)
