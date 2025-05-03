from django.conf import settings
from django.test import TestCase

from backend.utils.telegram import validate_telegram_mini_app_data
from twitter_downloader.utils import TwitterDownloader, TwitterDownloaderAPIV2


class TestTwitterDownloader(TestCase):
    def setUp(self):
        self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"
        self.tweet_url_2 = (
            "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️
        )

    def test_download_video(self):
        video_data = TwitterDownloader.get_video_data(self.tweet_url_1)

        self.assertIsNotNone(video_data)
        self.assertIsNotNone(video_data.get("id"), "Should contain ID")
        self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")
        self.assertIsNotNone(video_data.get("description"), "Should contain description")
        self.assertIsNotNone(video_data.get("videos"), "Should contain videos")

    def test_download_nsfw_video(self):
        video_data = TwitterDownloader.get_video_data(self.tweet_url_2)
        self.assertIsNotNone(video_data)
        self.assertIsNotNone(video_data.get("id"), "Should contain ID")
        self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")
        self.assertIsNotNone(video_data.get("description"), "Should contain description")
        self.assertIsNotNone(video_data.get("videos"), "Should contain videos")


class TestTwitterDownloaderAPIV2(TestCase):
    def setUp(self):
        self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"
        self.tweet_url_2 = (
            "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️
        )

    def test_get_tweet_data(self):
        twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_1)

        self.assertIsNotNone(twitter_downloader)
        self.assertIsNotNone(twitter_downloader.id, "Should contain ID")
        self.assertIsNotNone(twitter_downloader.description, "Should contain description")
        self.assertIsNotNone(twitter_downloader.data, "Should contain data")

    def test_get_nsfw_tweet_data(self):
        twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_2)

        self.assertIsNotNone(twitter_downloader)
        self.assertIsNotNone(twitter_downloader.id, "Should contain ID")
        self.assertIsNotNone(twitter_downloader.description, "Should contain description")
        self.assertIsNotNone(twitter_downloader.data, "Should contain data")


class TestValidateTelegramMiniAppData(TestCase):
    def test_validate_mini_app_data_true(self):
        telegram_bot_token = settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN
        init_data = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ec"

        result = validate_telegram_mini_app_data(init_data, telegram_bot_token)
        self.assertTrue(result)

    def test_validate_mini_app_data_false(self):
        telegram_bot_token = settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN
        init_data = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ecinvalid"

        with self.assertRaises(Exception) as cm:
            validate_telegram_mini_app_data(init_data, telegram_bot_token)

        self.assertIn("The given data hash is not valid!", str(cm.exception))
