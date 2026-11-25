from unittest.mock import Mock, patch

import requests
from django.test import TestCase

from tiktok.utils import TikHubAPI, TiktokVideoNoWatermark, send_to_private_telegram_channel


class TestTikHubAPI(TestCase):
    def setUp(self):
        self.tikhub = TikHubAPI()

    @patch("tiktok.utils.requests.request")
    def test__request(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"userInfo": {"user": {"uniqueId": "tiktok"}}}}
        mock_request.return_value = mock_response

        response = self.tikhub.request("/api/v1/tiktok/web/fetch_user_profile?uniqueId=tiktok")
        response_data = response.json().get("data")

        self.assertEqual(response.status_code, 200, "Should return 200 status code")
        self.assertIsNotNone(response_data, "Should not return empty data")

    @patch("tiktok.utils.requests.request")
    def test_get_user_id(self, mock_request):
        expected_sec_uid = "MS4wLjABAAAAPJwdzPJKzzNfqLlFTCqh4v8_zODCuUEbH4bNCELzegjPXmvN8pirTKmDo4wUzMVl"
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": {"userInfo": {"user": {"secUid": expected_sec_uid}}}}
        mock_request.return_value = mock_response

        user_id = self.tikhub.get_user_id("aangiehsl")
        self.assertEqual(user_id, expected_sec_uid)

    @patch("tiktok.utils.requests.request")
    def test_get_user_info(self, mock_request):
        expected_sec_uid = "MS4wLjABAAAAPJwdzPJKzzNfqLlFTCqh4v8_zODCuUEbH4bNCELzegjPXmvN8pirTKmDo4wUzMVl"

        # get_user_id response (fetch_user_profile)
        mock_response_user_id = Mock()
        mock_response_user_id.ok = True
        mock_response_user_id.json.return_value = {"data": {"userInfo": {"user": {"secUid": expected_sec_uid}}}}

        # get_user_info response (handler_user_profile)
        mock_response_user_info = Mock()
        mock_response_user_info.ok = True
        mock_response_user_info.json.return_value = {
            "data": {
                "user": {
                    "nickname": "Angie",
                    "unique_id": "aangiehsl",
                    "avatar_larger": {"url_list": ["https://example.com/avatar.jpg"]},
                    "follower_count": 1000,
                    "following_count": 500,
                    "visible_videos_count": 50,
                }
            }
        }

        # Clear cache so get_user_id makes an API call
        from django.core.cache import cache

        cache.delete("tiktok_user_id_aangiehsl")

        mock_request.side_effect = [mock_response_user_id, mock_response_user_info]

        user_info = self.tikhub.get_user_info("aangiehsl")
        self.assertEqual(user_info["username"], "aangiehsl", "Should return the correct username")


class TestTiktokRetryBehavior(TestCase):
    def setUp(self):
        self.client = TiktokVideoNoWatermark("aangiehsl")

    @patch("tiktok.utils.requests.request")
    def test_get_post_data_once_retries_and_succeeds(self, mock_request):
        ok_response = Mock()
        ok_response.json.return_value = {"data": {"videos": [{"video_id": "1"}]}}
        mock_request.side_effect = [
            requests.exceptions.RequestException("temporary error"),
            ok_response,
        ]

        with patch.object(TiktokVideoNoWatermark.get_post_data_once.retry, "sleep") as mock_sleep:
            data = self.client.get_post_data_once()

        self.assertEqual(data, {"videos": [{"video_id": "1"}]})
        self.assertEqual(mock_request.call_count, 2)
        mock_sleep.assert_called_once_with(10)

    @patch("tiktok.utils.requests.request")
    def test_get_post_data_once_reraises_after_max_attempts(self, mock_request):
        mock_request.side_effect = ValueError("upstream error")

        with patch.object(TiktokVideoNoWatermark.get_post_data_once.retry, "sleep") as mock_sleep:
            with self.assertRaises(ValueError):
                self.client.get_post_data_once()

        self.assertEqual(mock_request.call_count, 10)
        self.assertEqual(mock_sleep.call_count, 9)
        mock_sleep.assert_called_with(10)

    @patch("tiktok.utils.requests.request")
    def test_get_post_data_with_cursor_retries_and_reraises(self, mock_request):
        ok_response = Mock()
        ok_response.json.return_value = {"data": {"cursor": 50, "hasMore": False, "videos": []}}
        mock_request.side_effect = [
            requests.exceptions.Timeout("timeout"),
            ok_response,
        ]

        with patch.object(TiktokVideoNoWatermark.get_post_data_with_cursor.retry, "sleep") as mock_sleep:
            data = self.client.get_post_data_with_cursor(cursor=50)

        self.assertEqual(data["cursor"], 50)
        mock_sleep.assert_called_once_with(10)

        mock_request.side_effect = RuntimeError("fatal error")
        with patch.object(TiktokVideoNoWatermark.get_post_data_with_cursor.retry, "sleep") as mock_sleep:
            with self.assertRaises(RuntimeError):
                self.client.get_post_data_with_cursor(cursor=50)

        self.assertEqual(mock_sleep.call_count, 9)

    def test_get_all_post_retries_and_succeeds(self):
        with (
            patch.object(
                TiktokVideoNoWatermark,
                "get_post_data_once",
                side_effect=[
                    RuntimeError("transient error"),
                    {"cursor": 1, "hasMore": False, "videos": [{"video_id": "1"}]},
                ],
            ),
            patch.object(TiktokVideoNoWatermark.get_all_post.retry, "sleep") as mock_sleep,
        ):
            videos = self.client.get_all_post()

        self.assertEqual(videos, [{"video_id": "1"}])
        mock_sleep.assert_called_once_with(10)

    @patch("tiktok.utils.requests.request")
    def test_send_to_private_telegram_channel_retries_and_reraises(self, mock_request):
        ok_response = Mock(status_code=200)
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("connection reset"),
            requests.exceptions.ConnectionError("connection reset"),
            ok_response,
        ]

        with patch.object(send_to_private_telegram_channel.retry, "sleep") as mock_sleep:
            status_code = send_to_private_telegram_channel("https://example.com/video.mp4", "caption")

        self.assertEqual(status_code, 200)
        self.assertEqual(mock_request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(1)

        mock_request.reset_mock()
        mock_request.side_effect = requests.exceptions.ConnectionError("still down")

        with patch.object(send_to_private_telegram_channel.retry, "sleep") as mock_sleep:
            with self.assertRaises(requests.exceptions.ConnectionError):
                send_to_private_telegram_channel("https://example.com/video.mp4", "caption")

        self.assertEqual(mock_request.call_count, 10)
        self.assertEqual(mock_sleep.call_count, 9)
        mock_sleep.assert_called_with(1)
