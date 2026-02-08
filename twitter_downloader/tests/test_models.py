import time

from django.test import TestCase

from twitter_downloader.models import DownloadedTweet, ExternalLink, Settings, TelegramUser


class TestTelegramUserModel(TestCase):
    def setUp(self):
        self.telegram_user = TelegramUser.objects.create(
            user_id="939376599", first_name="Arter", last_name="Tendean", username="artertendean"
        )

    def test_send_chat_action(self):
        result = self.telegram_user.send_chat_action("typing")
        self.assertEqual(result, True, "Test send chat action")

    def test_send_message(self):
        result = self.telegram_user.send_message("Test Telegram user model")
        self.assertEqual(result, True)

    def test_send_document(self):
        result = self.telegram_user.send_document(
            "https://avatars.githubusercontent.com/u/9919", caption="Test document caption"
        )
        self.assertEqual(result, True)

    def test_send_maintenance_message(self):
        result = self.telegram_user.send_maintenance_message()
        self.assertEqual(result, True, "Test maintenance message")

    def test_send_banned_message(self):
        result = self.telegram_user.send_banned_message()
        self.assertEqual(result, True, "Test banned message")

    def test_send_photo(self):
        result = self.telegram_user.send_photo(
            {
                "thumbnail": "https://avatars.githubusercontent.com/u/9919",
                "videos": [{"url": "https://avatars.githubusercontent.com/u/9919", "size": 1337, "quality": "HD"}],
            }
        )
        self.assertEqual(result, True, "Test send photo")

    def test_send_video(self):
        result = self.telegram_user.send_video(
            {
                "thumbnail": "https://avatars.githubusercontent.com/u/9919",
                "description": "Test Send Video CI/CD",
                "videos": [{"url": "https://link.testfile.org/aXCg7h", "size": 1337, "quality": "HD"}],
            }
        )

        self.assertEqual(result, True, "Test send video")

    def test_send_download_button_with_safelink(self):
        result = self.telegram_user.send_download_button_with_safelink("Arter Tendean", "https://animemoe.us")
        self.assertEqual(result, True, "Sould return 200 OK (True)")

    def test_send_big_video(self):
        result = self.telegram_user.send_video(
            {
                "thumbnail": "https://avatars.githubusercontent.com/u/9919",
                "description": "Test Send Big VideoCI/CD",
                "videos": [
                    {
                        "url": "https://link.testfile.org/aYr11v",
                        "size": 1337,
                        "quality": "HD",
                    }
                ],
            }
        )

        self.assertEqual(result, True, "Test send video with big file size")

    def test_image_with_inline_url(self):
        result = self.telegram_user.send_image_with_inline_keyboard(
            image_url="https://avatars.githubusercontent.com/u/9919",
            inline_text="Arter Tendean",
            inline_url="https://avatars.githubusercontent.com/u/9919",
        )
        self.assertEqual(result, True, "Test send image with inline url")


class TestDownloadedTweet(TestCase):
    def setUp(self):
        self.telegram_user = TelegramUser.objects.create(
            user_id="939376599", first_name="Arter", last_name="Tendean", username="artertendean"
        )
        self.downloaded_tweet = DownloadedTweet.objects.create(
            telegram_user=self.telegram_user,
            tweet_url="http://twitter.com/",
            tweet_data={
                "id": "1832089399921619103",
                "videos": [
                    {
                        "url": "https://video.twimg.com/ext_tw_video/1832089368489504771/pu/vid/avc1/576x1024/li7koJg-y38Gc__b.mp4?tag=12",
                        "size": "576x1024",
                        "bitrate": 2176000,
                        "quality": "HD",
                    },
                    {
                        "url": "https://video.twimg.com/ext_tw_video/1832089368489504771/pu/vid/avc1/480x852/Fhx7X8Yz3m8dpOrs.mp4?tag=12",
                        "size": "480x852",
                        "bitrate": 950000,
                        "quality": "SD",
                    },
                    {
                        "url": "https://video.twimg.com/ext_tw_video/1832089368489504771/pu/vid/avc1/320x568/56e7jjUqebophPbI.mp4?tag=12",
                        "size": "320x568",
                        "bitrate": 632000,
                        "quality": "Low",
                    },
                ],
                "thumbnail": "https://pbs.twimg.com/ext_tw_video_thumb/1832089368489504771/pu/img/cGHHNJSF8wSp8Ygv.jpg",
                "description": "I don’t understand how some people still hate cats😭😭 https://t.co/qTOc612wOX",
            },
        )

    def test_sent_to_telegram_user(self):
        result = self.downloaded_tweet.send_to_telegram_user()
        self.assertEqual(result, True, "Should be able to send message")


class TestExternalLink(TestCase):
    def setUp(self):
        self.external_link_1 = ExternalLink.objects.create(title="Test External Link", url="https://api.animemoe.us")

    def test_get_external_link(self):
        queryset = ExternalLink.objects.all()
        self.assertEqual(queryset.count(), 1, "Should be able to get the external link data")


class TestSettings(TestCase):
    def test_settings(self):
        settings = Settings.get_solo()
        settings.webhook_url = "https://api.animemoe.us"
        settings.save()

        time.sleep(1)

        self.assertEqual(settings.set_webhook(), True, "Should set the webhook url successfully")
