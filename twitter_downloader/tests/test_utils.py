# from django.conf import settings  # noqa: ERA001
# from django.test import TestCase  # noqa: ERA001

# from core.utils.telegram import validate_telegram_mini_app_data  # noqa: ERA001
# from twitter_downloader.utils import TwitterDownloaderAPIV3, get_tweet_id_from_url  # noqa: E501, ERA001

# class TestTwitterDownloader(TestCase):
#     def setUp(self):
#         self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"  # noqa: E501, ERA001
#         self.tweet_url_2 = (
#             "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️  # noqa: E501, ERA001
#         )  # noqa: ERA001

#     def test_download_video(self):
#         video_data = TwitterDownloader.get_video_data(self.tweet_url_1)  # noqa: E501, ERA001

#         self.assertIsNotNone(video_data)  # noqa: ERA001
#         self.assertIsNotNone(video_data.get("id"), "Should contain ID")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("description"), "Should contain description")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("videos"), "Should contain videos")  # noqa: E501, ERA001

#     def test_download_nsfw_video(self):
#         video_data = TwitterDownloader.get_video_data(self.tweet_url_2)  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data)  # noqa: ERA001
#         self.assertIsNotNone(video_data.get("id"), "Should contain ID")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("thumbnail"), "Should contain thumbnail")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("description"), "Should contain description")  # noqa: E501, ERA001
#         self.assertIsNotNone(video_data.get("videos"), "Should contain videos")  # noqa: E501, ERA001


# class TestTwitterDownloaderAPIV2(TestCase):
#     def setUp(self):
#         self.tweet_url_1 = "https://x.com/tyomateee/status/1274296339375853568"  # noqa: E501, ERA001
#         self.tweet_url_2 = (
#             "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35"  # ☠️☠️☠️  # noqa: E501, ERA001
#         )  # noqa: ERA001

#     def test_get_tweet_data(self):
#         twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_1)  # noqa: ERA001

#         self.assertIsNotNone(twitter_downloader)  # noqa: ERA001
#         self.assertIsNotNone(twitter_downloader.id, "Should contain ID")  # noqa: E501, ERA001
#         self.assertIsNotNone(twitter_downloader.description, "Should contain description")  # noqa: E501, ERA001
#         self.assertIsNotNone(twitter_downloader.data, "Should contain data")  # noqa: E501, ERA001

#     def test_get_nsfw_tweet_data(self):
#         twitter_downloader = TwitterDownloaderAPIV2(self.tweet_url_2)  # noqa: ERA001

#         self.assertIsNotNone(twitter_downloader)  # noqa: ERA001
#         self.assertIsNotNone(twitter_downloader.id, "Should contain ID")  # noqa: E501, ERA001
#         self.assertIsNotNone(twitter_downloader.description, "Should contain description")  # noqa: E501, ERA001
#         self.assertIsNotNone(twitter_downloader.data, "Should contain data")  # noqa: E501, ERA001


# class TestTwitterDownloaderAPIV3(TestCase):
#     def setUp(self):
#         self.twitter_downloader = TwitterDownloaderAPIV3()  # noqa: ERA001
#         # Regular tweets with different content types
#         self.tweet_nsfw = "1918591364939632674"  # noqa: ERA001
#         self.tweet_image = "1918815845083447577"  # noqa: ERA001
#         self.tweet_multiple_video = "1916306205741617334"  # noqa: ERA001
#         self.tweet_gif = "1918759209983762736"  # noqa: ERA001
#         self.tweet_multiple_image = "1918227317752840298"  # noqa: ERA001

#     def test_nsfw_tweet(self):
#         """Test a tweet with NSFW content"""
#         tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_nsfw)  # noqa: E501, ERA001

#         self.assertIsNotNone(tweet_data)  # noqa: ERA001
#         self.assertEqual(tweet_data["tweet_id"], self.tweet_nsfw)  # noqa: ERA001
#         self.assertTrue(tweet_data["is_nsfw"], "Should be marked as NSFW")  # noqa: E501, ERA001
#         self.assertIsNotNone(tweet_data["text"], "Should contain text")  # noqa: E501, ERA001

#         # NSFW tweet usually has either photos or videos
#         self.assertTrue(
#             len(tweet_data["photos"]) > 0 or len(tweet_data["videos"]) > 0,  # noqa: E501, ERA001
#             "Should contain photos or videos",
#         )  # noqa: ERA001

#     def test_image_tweet(self):
#         """Test a tweet with a single image"""
#         tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_image)  # noqa: E501, ERA001

#         self.assertIsNotNone(tweet_data)  # noqa: ERA001
#         self.assertEqual(tweet_data["tweet_id"], self.tweet_image)  # noqa: ERA001
#         self.assertIsNotNone(tweet_data["text"], "Should contain text")  # noqa: E501, ERA001

#         # Should have photos
#         self.assertTrue(len(tweet_data["photos"]) > 0, "Should contain at least one photo")  # noqa: E501, ERA001
#         photo = tweet_data["photos"][0]  # noqa: ERA001
#         self.assertIsNotNone(photo, "Photo should not be None")  # noqa: ERA001

#     def test_multiple_video_tweet(self):
#         """Test a tweet with multiple videos"""
#         tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_multiple_video)  # noqa: E501, ERA001

#         self.assertIsNotNone(tweet_data)  # noqa: ERA001
#         self.assertEqual(tweet_data["tweet_id"], self.tweet_multiple_video)  # noqa: E501, ERA001
#         self.assertIsNotNone(tweet_data["text"], "Should contain text")  # noqa: E501, ERA001

#         # Should have videos
#         self.assertTrue(len(tweet_data["videos"]) > 0, "Should contain at least one video")  # noqa: E501, ERA001

#         # Check video structure
#         video = tweet_data["videos"][0]  # noqa: ERA001
#         self.assertIn("variants", video, "Video should have variants")  # noqa: ERA001
#         self.assertTrue(len(video["variants"]) > 0, "Should have at least one variant")  # noqa: E501, ERA001

#         variant = video["variants"][0]  # noqa: ERA001
#         self.assertIn("url", variant, "Variant should have URL")  # noqa: ERA001
#         self.assertIn("bitrate", variant, "Variant should have bitrate")  # noqa: E501, ERA001
#         self.assertIn("thumbnail", variant, "Variant should have thumbnail")  # noqa: E501, ERA001
#         self.assertIn("bitrate", variant, "Variant should have bitrate")  # noqa: E501, ERA001

#     def test_gif_tweet(self):
#         """Test a tweet with GIF content"""
#         tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_gif)  # noqa: E501, ERA001

#         self.assertIsNotNone(tweet_data)  # noqa: ERA001
#         self.assertEqual(tweet_data["tweet_id"], self.tweet_gif)  # noqa: ERA001
#         self.assertIsNotNone(tweet_data["text"], "Should contain text")  # noqa: E501, ERA001

#         # GIFs are usually stored as videos in Twitter's API
#         content_found = False  # noqa: ERA001
#         if len(tweet_data["videos"]) > 0:
#             content_found = True  # noqa: ERA001
#             video = tweet_data["videos"][0]  # noqa: ERA001
#             self.assertIn("variants", video, "Video/GIF should have variants")  # noqa: E501, ERA001

#         # Some APIs might return GIFs in a separate field or as photos
#         print("======tweet_data", tweet_data)  # noqa: ERA001
#         if "gifs" in tweet_data and len(tweet_data["gifs"]) > 0:
#             content_found = True  # noqa: ERA001
#             gif = tweet_data["gifs"][0]  # noqa: ERA001
#             self.assertIn("url", gif, "GIF should have URL")  # noqa: ERA001

#         self.assertTrue(content_found, "Should contain either videos or GIFs")  # noqa: E501, ERA001

#     def test_multiple_image_tweet(self):
#         """Test a tweet with multiple images"""
#         tweet_data = self.twitter_downloader.get_tweet_data(self.tweet_multiple_image)  # noqa: E501, ERA001

#         self.assertIsNotNone(tweet_data)  # noqa: ERA001
#         self.assertEqual(tweet_data["tweet_id"], self.tweet_multiple_image)  # noqa: E501, ERA001
#         self.assertIsNotNone(tweet_data["text"], "Should contain text")  # noqa: E501, ERA001

#         # Should have multiple photos
#         self.assertTrue(len(tweet_data["photos"]) > 1, "Should contain multiple photos")  # noqa: E501, ERA001

#         # Check photo structure
#         for photo in tweet_data["photos"]:
#             self.assertIsNotNone(photo, "Photo should not be None")  # noqa: ERA001

#     def test_extract_tweet_id_from_url(self):
#         """Test extracting tweet ID from various URL formats"""
#         url_formats = [  # noqa: ERA001
#             "https://x.com/username/status/1234567890",  # noqa: ERA001
#             "https://twitter.com/username/status/1234567890",  # noqa: ERA001
#             "https://x.com/username/status/1234567890?s=20&t=abcdef",  # noqa: ERA001
#             "https://twitter.com/username/status/1234567890/photo/1",  # noqa: ERA001
#         ]  # noqa: ERA001

#         for url in url_formats:
#             tweet_id = get_tweet_id_from_url(url)  # noqa: ERA001
#             self.assertEqual(tweet_id, "1234567890", f"Should extract ID 1234567890 from {url}")  # noqa: E501, ERA001


# class TestValidateTelegramMiniAppData(TestCase):
#     def test_validate_mini_app_data_true(self):
#         telegram_bot_token = settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN  # noqa: E501, ERA001
#         init_data = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ec"  # noqa: E501, ERA001

#         result = validate_telegram_mini_app_data(init_data, telegram_bot_token)  # noqa: E501, ERA001
#         self.assertTrue(result)  # noqa: ERA001

#     def test_validate_mini_app_data_false(self):
#         telegram_bot_token = settings.TWITTER_VIDEO_DOWNLOADER_BOT_TOKEN  # noqa: E501, ERA001
#         init_data = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ecinvalid"  # noqa: E501, ERA001

#         with self.assertRaises(Exception) as cm:
#             validate_telegram_mini_app_data(init_data, telegram_bot_token)  # noqa: E501, ERA001

#         self.assertIn("The given data hash is not valid!", str(cm.exception))  # noqa: E501, ERA001
