from django.test import TestCase, override_settings


class TestRoastingProfileView(TestCase):
    databases = {"default", "tidb"}

    def setUp(self):
        self.instagram_username = "angiehsl"

    @override_settings(DEBUG=True)
    def test_get_roasting(self):
        response = self.client.get(f"/instagram/roasting/{self.instagram_username}/?captcha=ARTERTENDEAN").json()
        print(response.get("roasting_text"))
        self.assertIsNotNone(response.get("roasting_text"))
