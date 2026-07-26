# from django.test import TestCase  # noqa: ERA001
# from django.urls import reverse  # noqa: ERA001

# from twitter_downloader.models import DownloadedTweet, TelegramUser  # noqa: ERA001


# class TestValidateTelegramMiniAppData(TestCase):
#     def setUp(self):
#         self.init_data_1 = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ec"  # noqa: E501, ERA001
#         self.init_data_2 = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ecinvalid"  # noqa: E501, ERA001

#     def test_validate_mini_app_data_success(self):
#         data = {"init_data": self.init_data_1}  # noqa: ERA001
#         response = self.client.post(  # noqa: ERA001
#             "/twitter-downloader/telegram-webhook/validate-mini-app-data/",
#             data,
#             format="json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 200, "Should return 200 OK")  # noqa: E501, ERA001

#     def test_validate_mini_app_data_failed(self):
#         data = {"init_data": self.init_data_2}  # noqa: ERA001
#         response = self.client.post(  # noqa: ERA001
#             "/twitter-downloader/telegram-webhook/validate-mini-app-data/",
#             data,
#             format="json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 400, "Should return 400 Bad Request")  # noqa: E501, ERA001


# class TestTelegramWebhookView(TestCase):
#     def setUp(self):
#         self.url = reverse("twitter-downloader:telegram-webhook")  # noqa: ERA001
#         self.text_message_payload = {
#             "update_id": 10000,  # noqa: ERA001
#             "message": {  # noqa: ERA001
#                 "date": 1441645532,  # noqa: ERA001
#                 "chat": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "message_id": 1365,  # noqa: ERA001
#                 "from": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "text": "/start",  # noqa: ERA001
#             },
#         }  # noqa: ERA001

#         self.edited_text_message_payload = {
#             "update_id": 10000,  # noqa: ERA001
#             "edited_message": {  # noqa: ERA001
#                 "date": 1441645532,  # noqa: ERA001
#                 "chat": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "message_id": 1365,  # noqa: ERA001
#                 "from": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "text": "/start",  # noqa: ERA001
#             },
#         }  # noqa: ERA001

#         self.text_message_with_tweet_payload = {
#             "update_id": 10000,  # noqa: ERA001
#             "message": {  # noqa: ERA001
#                 "date": 1441645532,  # noqa: ERA001
#                 "chat": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "message_id": 1365,  # noqa: ERA001
#                 "from": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "text": "https://x.com/tyomateee/status/1274296339375853568",  # noqa: E501, ERA001
#             },
#         }  # noqa: ERA001

#         self.text_message_with_nswf_tweet_payload = {
#             "update_id": 10000,  # noqa: ERA001
#             "message": {  # noqa: ERA001
#                 "date": 1441645532,  # noqa: ERA001
#                 "chat": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "message_id": 1365,  # noqa: ERA001
#                 "from": {  # noqa: ERA001
#                     "last_name": "Tendean",  # noqa: ERA001
#                     "id": 939376599,  # noqa: ERA001
#                     "first_name": "Arter",  # noqa: ERA001
#                     "username": "artertendean",  # noqa: ERA001
#                 },
#                 "text": "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35",  # noqa: E501, ERA001
#             },
#         }  # noqa: ERA001

#     def test_text_message(self):
#         self.assertEqual(TelegramUser.objects.all().count(), 0, "TelegramUser should be empty")  # noqa: E501, ERA001

#         response = self.client.post(  # noqa: ERA001
#             path=self.url,  # noqa: ERA001
#             data=self.text_message_payload,  # noqa: ERA001
#             content_type="application/json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001
#         self.assertEqual(TelegramUser.objects.all().count(), 1, "New TelegramUser should be created")  # noqa: E501, ERA001

#         response = self.client.post(  # noqa: ERA001
#             path=self.url,  # noqa: ERA001
#             data=self.edited_text_message_payload,  # noqa: ERA001
#             content_type="application/json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001
#         self.assertEqual(
#             TelegramUser.objects.all().count(),  # noqa: ERA001
#             1,
#             "New TelegramUser should not be created",
#         )  # noqa: ERA001

#     def test_text_message_with_tweet(self):
#         response = self.client.post(  # noqa: ERA001
#             path=self.url,  # noqa: ERA001
#             data=self.text_message_with_tweet_payload,  # noqa: ERA001
#             content_type="application/json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001
#         self.assertEqual(TelegramUser.objects.all().count(), 1, "New TelegramUser should be created")  # noqa: E501, ERA001
#         self.assertEqual(
#             DownloadedTweet.objects.all().count(),  # noqa: ERA001
#             1,
#             "New DownloadedTweet should be created",
#         )  # noqa: ERA001

#         response = self.client.post(  # noqa: ERA001
#             path=self.url,  # noqa: ERA001
#             data=self.text_message_with_nswf_tweet_payload,  # noqa: ERA001
#             content_type="application/json",  # noqa: ERA001
#         )  # noqa: ERA001
#         self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001
#         self.assertEqual(TelegramUser.objects.all().count(), 1, "TelegramUser should be updated")  # noqa: E501, ERA001
#         self.assertEqual(
#             DownloadedTweet.objects.all().count(),  # noqa: ERA001
#             2,
#             "New DownloadedTweet should be created",
#         )  # noqa: ERA001


# class TestSafelinkView(TestCase):
#     def setUp(self):
#         self.telegram_user = TelegramUser.objects.create(
#             user_id=939376599,  # noqa: ERA001
#             first_name="Arter",  # noqa: ERA001
#             last_name="Tendean",  # noqa: ERA001
#             username="artertendean",  # noqa: ERA001
#             is_active=True,  # noqa: ERA001
#         )  # noqa: ERA001
#         self.downloaded_tweet = DownloadedTweet.objects.create(
#             telegram_user=self.telegram_user,  # noqa: ERA001
#             tweet_url="https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35",  # noqa: E501, ERA001
#             tweet_data={  # noqa: ERA001
#                 "id": "1829443959665443131",  # noqa: ERA001
#                 "thumbnail": "https://pbs.twimg.com/amplify_video_thumb/1829017584693370880/img/P-8EHQzqpUma6HQg.jpg",  # noqa: E501, ERA001
#                 "description": "Towa Sengawa\nFull Movie https://t.co/jr8OIhKcza\n\n〉〉〉 Pakyokvip พักยกVIP 〈〈〈\n✔️ มวย บอล หวย จบครบในที่เดียว\n✔️ คาสิโน บาคาร่า Slot ครบทุกค่าย\n✔️ ระบบออโต้ รวดเร็วทันใจ\n✔️ เว็บตรง การเงินมั่นคง 100%\n✔️สมัครเลย &gt;&gt; https://t.co/z3urv4YdNF https://t.co/97uuzuks4G",  # noqa: E501, ERA001
#                 "videos": [
#                     {  # noqa: ERA001
#                         "bitrate": 2176000,  # noqa: ERA001
#                         "size": "1280x720",  # noqa: ERA001
#                         "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/1280x720/jUfa2gTltPKwdD7X.mp4?tag=14",  # noqa: E501, ERA001
#                     },
#                     {  # noqa: ERA001
#                         "bitrate": 832000,  # noqa: ERA001
#                         "size": "640x360",  # noqa: ERA001
#                         "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/640x360/ooWBMl6bFgHptgvR.mp4?tag=14",  # noqa: E501, ERA001
#                     },
#                     {  # noqa: ERA001
#                         "bitrate": 288000,  # noqa: ERA001
#                         "size": "480x270",  # noqa: ERA001
#                         "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/480x270/S0jeAUFxoo4rvYfn.mp4?tag=14",  # noqa: E501, ERA001
#                     },
#                 ],
#             },
#         )  # noqa: ERA001

#     def test_get_safelink(self):
#         url = f"{reverse('twitter-downloader:safelink')}?key={self.downloaded_tweet.uuid}"  # noqa: E501, ERA001
#         response = self.client.get(url)  # noqa: ERA001

#         self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001

#     # def test_post_safelink(self):
#     #     url = reverse("twitter-downloader:safelink")  # noqa: ERA001
#     #     response = self.client.post(url, data={"uuid": DownloadedTweet.objects.first().uuid})  # noqa: E501, ERA001

#     #     self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")  # noqa: E501, ERA001

#     # TODO: add test for invalid UUID
