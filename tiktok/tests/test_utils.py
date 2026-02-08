from unittest.mock import Mock, patch

from django.test import TestCase

from tiktok.utils import TikHubAPI


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
