from unittest.mock import Mock, patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from waifu.utils import generate_image_embedding, refresh_expired_urls, refresh_serializer_data_urls


class TestRefreshExpiredURLS(TestCase):
    def setUp(self):
        self.expired_urls_1 = [
            "https://64.media.tumblr.com/3a7de325951453a7a3ad41ea992d2c4c/5920cbbca6af3345-51/s1280x1920/365844bab8106ae227d1503cb003980c4cb7ef68.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631722272260148/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631652307075165/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631496677298217/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631492734783579/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631444743426079/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631263373590539/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631260349235283/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275631208495321088/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275630951610716161/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1275630850230190262/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1270956343318151188/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1270956079114747999/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1270955995539046520/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1270955850701471835/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1268536242601988117/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1268536194275344434/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1268536157218668638/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1268536102961020988/animemoeus-waifu.jpg",
            "https://cdn.discordapp.com/attachments/858938620425404426/1268536085483356193/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631722272260148/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631652307075165/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631496677298217/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631492734783579/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631444743426079/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631263373590539/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631260349235283/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275631208495321088/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275630951610716161/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1275630850230190262/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1270956343318151188/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1270956079114747999/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1270955995539046520/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1270955850701471835/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1268536242601988117/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1268536194275344434/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1268536157218668638/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1268536102961020988/animemoeus-waifu.jpg",
            "https://media.discordapp.net/attachments/858938620425404426/1268536085483356193/animemoeus-waifu.jpg",
        ]

    @patch("waifu.utils.requests.request")
    def test_refresh_expired_urls(self, mock_request):
        # Build a response that maps each URL to a refreshed version
        refreshed_urls_response = [
            {"original": url, "refreshed": url + "?refreshed=true"} for url in self.expired_urls_1
        ]
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"refreshed_urls": refreshed_urls_response}
        mock_request.return_value = mock_response

        refreshed_urls = refresh_expired_urls(self.expired_urls_1)
        self.assertEqual(len(refreshed_urls), 41, "Should return 41 refreshed URLs")


class TestRefreshSerializerDataURLS(TestCase):
    def setUp(self):
        self.serializer_data = [
            {
                "image_id": "1",
                "original_image": "https://cdn.discordapp.com/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
                "thumbnail": "https://media.discordapp.net/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
            },
            {
                "image_id": "2",
                "original_image": "https://cdn.discordapp.com/attachments/858938620425404426/1275631722272260148/animemoeus-waifu.jpg",
                "thumbnail": "https://media.discordapp.net/attachments/858938620425404426/1275631722272260148/animemoeus-waifu.jpg",
            },
            {
                "image_id": "3",
                "original_image": "https://cdn.discordapp.com/attachments/858938620425404426/1275631652307075165/animemoeus-waifu.jpg",
                "thumbnail": "https://media.discordapp.net/attachments/858938620425404426/1275631652307075165/animemoeus-waifu.jpg",
            },
            {
                "image_id": "4",
                "original_image": "https://cdn.discordapp.com/attachments/858938620425404426/1275631496677298217/animemoeus-waifu.jpg",
                "thumbnail": "https://media.discordapp.net/attachments/858938620425404426/1275631496677298217/animemoeus-waifu.jpg",
            },
            {
                "image_id": "5",
                "original_image": "https://cdn.discordapp.com/attachments/858938620425404426/1275631492734783579/animemoeus-waifu.jpg",
                "thumbnail": "https://media.discordapp.net/attachments/858938620425404426/1275631492734783579/animemoeus-waifu.jpg",
            },
        ]

    @patch("waifu.utils.requests.request")
    def test_refresh_serializer_data_urls(self, mock_request):
        # Collect all URLs that will be passed to refresh_expired_urls
        urls = []
        for item in self.serializer_data:
            urls.append(item["original_image"])
            urls.append(item["thumbnail"])

        refreshed_urls_response = [{"original": url, "refreshed": url + "?refreshed=true"} for url in urls]
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"refreshed_urls": refreshed_urls_response}
        mock_request.return_value = mock_response

        refreshed_serializer_data = refresh_serializer_data_urls(self.serializer_data)

        # Verify URLs were refreshed (have ?refreshed=true appended)
        self.assertIn("?refreshed=true", refreshed_serializer_data[0]["original_image"])


class TestGenerateImageEmbedding(TestCase):
    def _make_setting(self, api_key="test-api-key"):
        setting = Mock()
        setting.embedding_api_key = api_key
        setting.openrouter_base_url = "https://openrouter.ai"
        setting.embedding_model = "google/gemini-embedding-2"
        return setting

    @patch("waifu.utils.Setting")
    def test_empty_url_raises_value_error(self, mock_setting_cls):
        with self.assertRaises(ValueError):
            generate_image_embedding("")

    @patch("waifu.utils.Setting")
    def test_whitespace_url_raises_value_error(self, mock_setting_cls):
        with self.assertRaises(ValueError):
            generate_image_embedding("   ")

    @patch("waifu.utils.Setting")
    def test_missing_api_key_raises_improperly_configured(self, mock_setting_cls):
        mock_setting_cls.get_solo.return_value = self._make_setting(api_key="")
        with self.assertRaises(ImproperlyConfigured):
            generate_image_embedding("https://example.com/image.jpg")

    @patch("waifu.utils.requests.post")
    @patch("waifu.utils.Setting")
    def test_successful_response_returns_embedding_and_token_usage(self, mock_setting_cls, mock_post):
        mock_setting_cls.get_solo.return_value = self._make_setting()

        embedding_vector = [0.1, 0.2, 0.3]
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"embedding": embedding_vector}],
            "usage": {"total_tokens": 42},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        embedding, token_usage = generate_image_embedding("https://example.com/image.jpg")

        self.assertEqual(embedding, embedding_vector)
        self.assertEqual(token_usage, 42)
