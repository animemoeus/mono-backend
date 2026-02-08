from unittest.mock import Mock, patch

from django.test import TestCase

from tiktok.models import User as TikTokUser


class TestTikTokUser(TestCase):
    def setUp(self):
        self.user = TikTokUser.objects.create(username="arter_tendean")

    @patch("tiktok.models.requests.get")
    @patch("tiktok.utils.requests.request")
    def test_update_data_from_api(self, mock_request, mock_get):
        expected_sec_uid = "MS4wLjABAAAAtest123"

        # First call: get_user_id (fetch_user_profile)
        mock_response_1 = Mock()
        mock_response_1.ok = True
        mock_response_1.json.return_value = {"data": {"userInfo": {"user": {"secUid": expected_sec_uid}}}}

        # Second call: get_user_info (handler_user_profile)
        mock_response_2 = Mock()
        mock_response_2.ok = True
        mock_response_2.json.return_value = {
            "data": {
                "user": {
                    "nickname": "Arter Tendean",
                    "unique_id": "arter_tendean",
                    "avatar_larger": {"url_list": ["https://example.com/avatar.jpg"]},
                    "follower_count": 100,
                    "following_count": 50,
                    "visible_videos_count": 10,
                }
            }
        }

        mock_request.side_effect = [mock_response_1, mock_response_2]

        # Mock avatar download
        mock_avatar_response = Mock()
        mock_avatar_response.ok = False  # Skip actual file save
        mock_get.return_value = mock_avatar_response

        self.user.update_data_from_api()
        self.assertNotEqual(self.user.user_id, "")
        self.assertNotEqual(self.user.avatar_url, "")
