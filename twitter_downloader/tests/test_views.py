from django.test import TestCase
from django.urls import reverse

from twitter_downloader.models import DownloadedTweet, TelegramUser


class TestValidateTelegramMiniAppData(TestCase):
    def setUp(self):
        self.init_data_1 = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ec"
        self.init_data_2 = "query_id=AAHXv_03AAAAANe__TfVCFD_&user=%7B%22id%22%3A939376599%2C%22first_name%22%3A%22arterrr%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22artertendean%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1723083100&hash=83dae1980c08b7706c4f572eef937c10f885101eb1f56848203ba88e7cd708ecinvalid"

    def test_validate_mini_app_data_success(self):
        data = {"init_data": self.init_data_1}
        response = self.client.post(
            "/twitter-downloader/telegram-webhook/validate-mini-app-data/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

    def test_validate_mini_app_data_failed(self):
        data = {"init_data": self.init_data_2}
        response = self.client.post(
            "/twitter-downloader/telegram-webhook/validate-mini-app-data/",
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 400, "Should return 400 Bad Request")


class TestTelegramWebhookView(TestCase):
    def setUp(self):
        self.url = reverse("twitter-downloader:telegram-webhook")
        self.text_message_payload = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "text": "/start",
            },
        }

        self.edited_text_message_payload = {
            "update_id": 10000,
            "edited_message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "text": "/start",
            },
        }

        self.text_message_with_tweet_payload = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "text": "https://x.com/tyomateee/status/1274296339375853568",
            },
        }

        self.text_message_with_nswf_tweet_payload = {
            "update_id": 10000,
            "message": {
                "date": 1441645532,
                "chat": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "message_id": 1365,
                "from": {
                    "last_name": "Tendean",
                    "id": 939376599,
                    "first_name": "Arter",
                    "username": "artertendean",
                },
                "text": "https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35",
            },
        }

    def test_text_message(self):
        self.assertEqual(TelegramUser.objects.all().count(), 0, "TelegramUser should be empty")

        response = self.client.post(
            path=self.url,
            data=self.text_message_payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")
        self.assertEqual(TelegramUser.objects.all().count(), 1, "New TelegramUser should be created")

        response = self.client.post(
            path=self.url,
            data=self.edited_text_message_payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")
        self.assertEqual(
            TelegramUser.objects.all().count(),
            1,
            "New TelegramUser should not be created",
        )

    def test_text_message_with_tweet(self):
        response = self.client.post(
            path=self.url,
            data=self.text_message_with_tweet_payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")
        self.assertEqual(TelegramUser.objects.all().count(), 1, "New TelegramUser should be created")
        self.assertEqual(
            DownloadedTweet.objects.all().count(),
            1,
            "New DownloadedTweet should be created",
        )

        response = self.client.post(
            path=self.url,
            data=self.text_message_with_nswf_tweet_payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")
        self.assertEqual(TelegramUser.objects.all().count(), 1, "TelegramUser should be updated")
        self.assertEqual(
            DownloadedTweet.objects.all().count(),
            2,
            "New DownloadedTweet should be created",
        )


class TestSafelinkView(TestCase):
    def setUp(self):
        self.telegram_user = TelegramUser.objects.create(
            user_id=939376599,
            first_name="Arter",
            last_name="Tendean",
            username="artertendean",
            is_active=True,
        )
        self.downloaded_tweet = DownloadedTweet.objects.create(
            telegram_user=self.telegram_user,
            tweet_url="https://x.com/WarpsiwaAV/status/1829443959665443131?t=kZOlgjU0EJ-FAEol6Ij22Q&s=35",
            tweet_data={
                "id": "1829443959665443131",
                "thumbnail": "https://pbs.twimg.com/amplify_video_thumb/1829017584693370880/img/P-8EHQzqpUma6HQg.jpg",
                "description": "Towa Sengawa\nFull Movie https://t.co/jr8OIhKcza\n\n〉〉〉 Pakyokvip พักยกVIP 〈〈〈\n✔️ มวย บอล หวย จบครบในที่เดียว\n✔️ คาสิโน บาคาร่า Slot ครบทุกค่าย\n✔️ ระบบออโต้ รวดเร็วทันใจ\n✔️ เว็บตรง การเงินมั่นคง 100%\n✔️สมัครเลย &gt;&gt; https://t.co/z3urv4YdNF https://t.co/97uuzuks4G",
                "videos": [
                    {
                        "bitrate": 2176000,
                        "size": "1280x720",
                        "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/1280x720/jUfa2gTltPKwdD7X.mp4?tag=14",
                    },
                    {
                        "bitrate": 832000,
                        "size": "640x360",
                        "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/640x360/ooWBMl6bFgHptgvR.mp4?tag=14",
                    },
                    {
                        "bitrate": 288000,
                        "size": "480x270",
                        "url": "https://video.twimg.com/amplify_video/1829017584693370880/vid/avc1/480x270/S0jeAUFxoo4rvYfn.mp4?tag=14",
                    },
                ],
            },
        )

    def test_get_safelink(self):
        url = f"{reverse('twitter-downloader:safelink')}?key={self.downloaded_tweet.uuid}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")

    # def test_post_safelink(self):
    #     url = reverse("twitter-downloader:safelink")
    #     response = self.client.post(url, data={"uuid": DownloadedTweet.objects.first().uuid})

    #     self.assertEqual(response.status_code, 200, "Response status code should be 200 (OK)")

    # TODO: add test for invalid UUID
