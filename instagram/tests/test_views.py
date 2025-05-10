from django.test import TestCase


class TestRoastingProfileView(TestCase):
    def setUp(self):
        self.instagram_username = "angiehsl"

    # @override_settings(DEBUG=True)
    # def test_get_roasting(self):
    #     response = self.client.get(f"/instagram/roasting/{self.instagram_username}/?captcha=ARTERTENDEAN").json()
    #     print(response.get("roasting_text"))
    #     self.assertIsNotNone(response.get("roasting_text"))
