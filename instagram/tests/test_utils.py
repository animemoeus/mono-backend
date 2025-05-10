from django.test import TestCase

from instagram.utils import InstagramAPI


class TestInstagramAPI(TestCase):
    def setUp(self):
        self.instagram_api = InstagramAPI()
        self.test_user_1 = "angiehsl"

    def test_get_user_info_v2(self):
        user_info = self.instagram_api.get_user_info_v2(self.test_user_1)
        self.assertIsNotNone(user_info, "Should return user information")

    def test_get_user_info_by_id_v2(self):
        user_info = self.instagram_api.get_user_info_by_id_v2("1731393118")
        self.assertIsNotNone(user_info, "Should return user information")

    def test_get_user_stories(self):
        status_code, stories = self.instagram_api.get_user_stories(self.test_user_1)
        self.assertIsNotNone(stories, "Should return user stories")

    def test_get_account_privacy(self):
        is_private_account = self.instagram_api.is_private_account("xtra.artx")
        self.assertEqual(is_private_account, True)

    def test_get_user_followers(self):
        followers = self.instagram_api.get_user_followers("xtra.artx")
        self.assertEqual(type(followers), list)

    def test_get_user_following(self):
        following = self.instagram_api.get_user_following("xtra.artx")
        self.assertEqual(type(following), list)


# class TestGetInstagramRoastingText(TestCase):
#     def setUp(self):
#         self.instagram_api = InstagramAPI()
#         self.instagram_user_data = self.instagram_api.get_user_info_v2("aenjies")

#     def test_get_profile_picture_keywords(self):
#         profile_picture_keywords = RoastingIG.get_profile_picture_keywords(
#             self.instagram_user_data.get("profile_pic_url")
#         )
#         self.assertIsNotNone(profile_picture_keywords, "Should return profile picture keywords")

#     def test_get_instagram_roasting_text(self):
#         roasting_text = RoastingIG.get_instagram_roasting_text(self.instagram_user_data)
#         self.assertIsNotNone(roasting_text, "Should return roasting text")
