from unittest.mock import patch

from django.test import TestCase


class TestDiscordRefreshURL(TestCase):
    def setUp(self):
        self.expired_url = (
            "https://cdn.discordapp.com/attachments/858938620425404426/1248453128991412224/animemoeus-waifu.jpg"
        )
        self.invalid_url = "https://google.com"

    @patch("discord.ninja.DiscordAPI.refresh_url")
    def test_refresh_expired_url(self, mock_refresh):
        mock_refresh.return_value = "https://cdn.discordapp.com/attachments/refreshed-url.jpg"

        # request using the refresher API
        response = self.client.get(f"/discord/refresh/?url={self.expired_url}")
        self.assertEqual(response.status_code, 302)

        # verify redirect URL is the refreshed URL
        self.assertEqual(response.url, "https://cdn.discordapp.com/attachments/refreshed-url.jpg")

    @patch("discord.ninja.DiscordAPI.refresh_url")
    def test_refresh_invalid_url(self, mock_refresh):
        mock_refresh.return_value = None
        response = self.client.get(f"/discord/refresh/?url={self.invalid_url}")
        self.assertEqual(response.status_code, 444)
