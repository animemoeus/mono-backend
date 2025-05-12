from unittest.mock import MagicMock, patch

from django.test import TestCase

from instagram.utils import InstagramAPI, RoastingIG


class TestInstagramAPI(TestCase):
    def setUp(self):
        self.instagram_api = InstagramAPI()
        self.test_user_1 = "arter_tendean"
        self.test_user_2 = "xtra.artx"

    def test_get_user_info_v2(self):
        """Test the get_user_info_v2 method returns expected user data structure"""
        # Get user info for test_user_1
        user_info = self.instagram_api.get_user_info_v2(self.test_user_1)

        # Check that we got a valid response
        self.assertIsNotNone(user_info)
        self.assertIsInstance(user_info, dict)

        # Check for essential fields in the response
        self.assertIn("username", user_info)
        self.assertEqual(user_info["username"], self.test_user_1)

        # Check other important fields
        self.assertIn("profile_pic_url", user_info)
        self.assertIn("is_private", user_info)
        self.assertIn("follower_count", user_info)
        self.assertIn("following_count", user_info)
        self.assertIn("media_count", user_info)

        # Check for the user ID field
        self.assertIn("pk", user_info)
        self.assertTrue(user_info["pk"].isdigit())

    def test_get_user_info_v2_detailed_structure(self):
        """Test the detailed structure of the get_user_info_v2 response"""
        # Get user info for test_user_1
        user_info = self.instagram_api.get_user_info_v2(self.test_user_1)

        # Check all required fields from the API response example
        required_fields = [
            "full_name",
            "is_private",
            "username",
            "profile_pic_url",
            "hd_profile_pic_url_info",
            "biography",
            "external_url",
            "follower_count",
            "following_count",
            "media_count",
            "pk",
            "id",
            "account_type",
        ]

        for field in required_fields:
            self.assertIn(field, user_info, f"Missing required field: {field}")

        # Check nested field structure
        self.assertIsInstance(user_info["hd_profile_pic_url_info"], dict)
        self.assertIn("url", user_info["hd_profile_pic_url_info"])

        # Check for bio links if they exist
        if "bio_links" in user_info and user_info["bio_links"]:
            self.assertIsInstance(user_info["bio_links"], list)
            if user_info["bio_links"]:
                first_link = user_info["bio_links"][0]
                self.assertIn("url", first_link)
                self.assertIn("link_type", first_link)

    def test_get_user_info_v2_error_handling(self):
        """Test the error handling of get_user_info_v2 with an invalid username"""
        # Testing with a username that doesn't exist (random string)
        with self.assertRaises(Exception):
            self.instagram_api.get_user_info_v2("this_user_definitely_doesnt_exist_12345678909876543")

    def test_is_private_account(self):
        """Test the is_private_account method for both private and public accounts"""
        # Test user 1 (should return whether the account is private or not)
        is_private_1 = self.instagram_api.is_private_account(self.test_user_1)
        self.assertIsNotNone(is_private_1, "Should return a boolean value for is_private")
        self.assertIsInstance(is_private_1, bool, "Result should be a boolean")

        # Test user 2 (should return whether the account is private or not)
        is_private_2 = self.instagram_api.is_private_account(self.test_user_2)
        self.assertIsNotNone(is_private_2, "Should return a boolean value for is_private")
        self.assertIsInstance(is_private_2, bool, "Result should be a boolean")


class TestGetInstagramRoastingText(TestCase):
    def setUp(self):
        self.instagram_api = InstagramAPI()
        self.instagram_user_data = self.instagram_api.get_user_info_v2("aenjies")

    def test_get_profile_picture_keywords(self):
        profile_picture_keywords = RoastingIG.get_profile_picture_keywords(
            self.instagram_user_data.get("profile_pic_url")
        )
        self.assertIsNotNone(profile_picture_keywords, "Should return profile picture keywords")

    def test_get_instagram_roasting_text(self):
        roasting_text = RoastingIG.get_instagram_roasting_text(self.instagram_user_data)
        self.assertIsNotNone(roasting_text, "Should return roasting text")


class TestInstagramAPIWithMock(TestCase):
    """Tests for InstagramAPI that use mocking to avoid actual API calls"""

    def setUp(self):
        self.instagram_api = InstagramAPI()
        self.test_username = "arter_tendean"

        # Sample response data based on the provided API response
        self.mock_user_data = {
            "status": True,
            "full_name": "",
            "is_private": False,
            "username": "arter_tendean",
            "pk": "1731393118",
            "profile_pic_url": "https://example.com/profile.jpg",
            "hd_profile_pic_url_info": {"url": "https://example.com/hd_profile.jpg"},
            "biography": "Sofwae Enginyeew (⁠ㆁ⁠ω⁠ㆁ⁠)",
            "bio_links": [{"link_type": "external", "url": "http://animemoe.us"}],
            "external_url": "http://animemoe.us",
            "account_type": 3,
            "follower_count": 5653,
            "following_count": 154,
            "media_count": 10,
            "id": "1731393118",
        }

        # Sample API response structure
        self.mock_api_response = {
            "code": 200,
            "router": "/api/v1/instagram/web_app/fetch_user_info_by_username_v2",
            "params": {"username": self.test_username},
            "data": self.mock_user_data,
        }

    @patch("requests.get")
    def test_get_user_info_v2_with_mock(self, mock_get):
        """Test get_user_info_v2 with mocked API response"""
        # Configure the mock to return a specific response when called
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_response

        # Call the method with the test username
        result = self.instagram_api.get_user_info_v2(self.test_username)

        # Verify the requests.get was called with expected args
        expected_url = self.instagram_api.base_url + "/api/v1/instagram/web_app/fetch_user_info_by_username_v2"
        expected_params = {"username": self.test_username}

        mock_get.assert_called_once_with(
            expected_url,
            headers=self.instagram_api.headers,
            params=expected_params,
            timeout=self.instagram_api.REQUEST_TIMEOUT,
        )

        # Check the result against our mock data
        self.assertEqual(result, self.mock_user_data)

    @patch("requests.get")
    def test_get_user_info_v2_error_handling_with_mock(self, mock_get):
        """Test error handling in get_user_info_v2 with mocked error response"""
        # Configure the mock to return an error response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.instagram_api.get_user_info_v2(self.test_username)

        # Verify the exception contains the status code
        self.assertIn("404", str(context.exception))
