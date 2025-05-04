from django.conf import settings
from django.test import TestCase

from backend.utils.telegram import validate_telegram_mini_app_data
from twitter_downloader.utils import TwitterDownloaderAPIV3, get_tweet_id_from_url

# class TestTwitterDownloader(TestCase):
#     def setUp(self):
#         self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"
#         self.tweet_url_2 = (
#             "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️
#         )

#     def test_download_video(self):
#         video_data = TwitterDownloader.get_video_data(self.tweet_url_1)

#         self.assertIsNotNone(video_data)
#         self.assertIsNotNone(video_data.get("id"), "Should contain ID")
#         self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")
#         self.assertIsNotNone(video_data.get("description"), "Should contain description")
#         self.assertIsNotNone(video_data.get("videos"), "Should contain videos")

#     def test_download_nsfw_video(self):
#         video_data = TwitterDownloader.get_video_data(self.tweet_url_2)
#         self.assertIsNotNone(video_data)
#         self.assertIsNotNone(video_data.get("id"), "Should contain ID")
#         self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")
#         self.assertIsNotNone(video_data.get("description"), "Should contain description")
#         self.assertIsNotNone(video_data.get("videos"), "Should contain videos")


# class TestTwitterDownloaderAPIV2(TestCase):
#     def setUp(self):
#         self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"
#         self.tweet_url_2 = (
#             "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️
#         )

#     def test_get_tweet_data(self):
#         twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_1)

#         self.assertIsNotNone(twitter_downloader)
#         self.assertIsNotNone(twitter_downloader.id, "Should contain ID")
#         self.assertIsNotNone(twitter_downloader.description, "Should contain description")
#         self.assertIsNotNone(twitter_downloader.data, "Should contain data")

#     def test_get_nsfw_tweet_data(self):
#         twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_2)

#         self.assertIsNotNone(twitter_downloader)
#         self.assertIsNotNone(twitter_downloader.id, "Should contain ID")
#         self.assertIsNotNone(twitter_downloader.description, "Should contain description")
#         self.assertIsNotNone(twitter_downloader.data, "Should contain data")


class TestTwitterDownloaderAPIV3(TestCase):
    def setUp(self):
        self.twitter_downloader = TwitterDownloaderAPIV3()
        # Regular tweets with different content types
        self.tweet_nsfw = "1918591364939632674"
        self.tweet_image = "1918815845083447577"
        self.tweet_multiple_video = "1916306205741617334"
        self.tweet_gif = "1918759209983762736"
        self.tweet_multiple_image = "1918227317752840298"

    def test_nsfw_tweet(self):
        """Test a tweet with NSFW content"""
        tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_nsfw)

        self.assertIsNotNone(tweet_data)
        self.assertEqual(tweet_data["tweet_id"], self.tweet_nsfw)
        self.assertTrue(tweet_data["is_nsfw"], "Should be marked as NSFW")
        self.assertIsNotNone(tweet_data["text"], "Should contain text")

        # NSFW tweet usually has either photos or videos
        self.assertTrue(
            len(tweet_data["photos"]) > 0 or len(tweet_data["videos"]) > 0,
            "Should contain photos or videos",
        )

    def test_image_tweet(self):
        """Test a tweet with a single image"""
        tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_image)

        self.assertIsNotNone(tweet_data)
        self.assertEqual(tweet_data["tweet_id"], self.tweet_image)
        self.assertIsNotNone(tweet_data["text"], "Should contain text")

        # Should have photos
        self.assertTrue(len(tweet_data["photos"]) > 0, "Should contain at least one photo")
        photo = tweet_data["photos"][0]
        self.assertIsNotNone(photo, "Photo should not be None")

    def test_multiple_video_tweet(self):
        """Test a tweet with multiple videos"""
        tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_multiple_video)

        self.assertIsNotNone(tweet_data)
        self.assertEqual(tweet_data["tweet_id"], self.tweet_multiple_video)
        self.assertIsNotNone(tweet_data["text"], "Should contain text")

        # Should have videos
        self.assertTrue(len(tweet_data["videos"]) > 0, "Should contain at least one video")

        # Check video structure
        video = tweet_data["videos"][0]
        self.assertIn("variants", video, "Video should have variants")
        self.assertTrue(len(video["variants"]) > 0, "Should have at least one variant")

        variant = video["variants"][0]
        self.assertIn("url", variant, "Variant should have URL")
        self.assertIn("bitrate", variant, "Variant should have bitrate")
        self.assertIn("thumbnail", variant, "Variant should have thumbnail")
        self.assertIn("bitrate", variant, "Variant should have bitrate")

    def test_gif_tweet(self):
        """Test a tweet with GIF content"""
        tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_gif)

        self.assertIsNotNone(tweet_data)
        self.assertEqual(tweet_data["tweet_id"], self.tweet_gif)
        self.assertIsNotNone(tweet_data["text"], "Should contain text")

        # GIFs are usually stored as videos in Twitter's API
        content_found = False
        if len(tweet_data["videos"]) > 0:
            content_found = True
            video = tweet_data["videos"][0]
            self.assertIn("variants", video, "Video/GIF should have variants")

        # Some APIs might return GIFs in a separate field or as photos
        print("======tweet_data", tweet_data)
        if "gifs" in tweet_data and len(tweet_data["gifs"]) > 0:
            content_found = True
            gif = tweet_data["gifs"][0]
            self.assertIn("url", gif, "GIF should have URL")

        self.assertTrue(content_found, "Should contain either videos or GIFs")

    def test_multiple_image_tweet(self):
        """Test a tweet with multiple images"""
        tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_multiple_image)

        self.assertIsNotNone(tweet_data)
        self.assertEqual(tweet_data["tweet_id"], self.tweet_multiple_image)
        self.assertIsNotNone(tweet_data["text"], "Should contain text")

        # Should have multiple photos
        self.assertTrue(len(tweet_data["photos"]) > 1, "Should contain multiple photos")

        # Check photo structure
        for photo in tweet_data["photos"]:
            self.assertIsNotNone(photo, "Photo should not be None")

    def test_extract_tweet_id_from_url(self):
        """Test extracting tweet ID from various URL formats"""
        url_formats = [
            "https://x.com/username/status/1234567890",
            "https://twitter.com/username/status/1234567890",
            "https://x.com/username/status/1234567890?s=20&t=abcdef",
            "https://twitter.com/username/status/1234567890/photo/1",
        ]

        for url in url_formats:
            tweet_id = get_tweet_id_from_url(url)
            self.assertEqual(tweet_id, "1234567890", f"Should extract ID 1234567890 from {url}")


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
