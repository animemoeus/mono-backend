from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from waifu.models import Image


def create_waifu_init_data():
    Image.objects.create(
        image_id="626173987744104449",
        original_image="https://64.media.tumblr.com/3a7de325951453a7a3ad41ea992d2c4c/5920cbbca6af3345-51/s1280x1920/365844bab8106ae227d1503cb003980c4cb7ef68.jpg",
        thumbnail="https://64.media.tumblr.com/3a7de325951453a7a3ad41ea992d2c4c/5920cbbca6af3345-51/s540x810/6310e4c616853144c28535f50b3617a991bbc633.jpg",
        is_nsfw=False,
        width=843,
        height=1199,
        creator_name="うーろん汰",
        creator_username="U_ronnta",
        caption="",
        source="",
    )

    Image.objects.create(
        image_id="1275631907933261897",
        original_image="https://cdn.discordapp.com/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
        thumbnail="https://media.discordapp.net/attachments/858938620425404426/1275631907933261897/animemoeus-waifu.jpg",
        is_nsfw=False,
        width=768,
        height=1024,
        creator_name="kouko",
        creator_username="user_srze7285",
        caption="高木さん_からかい上手の高木さん",
        source="https://www.pixiv.net/en/artworks/118510411",
    )


@patch("waifu.views.refresh_serializer_data_urls", side_effect=lambda data: data)
class TestWaifuListView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_waifu_list(self, mock_refresh):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:index"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json().get("results")[0]
        self.assertIn("original_image", data)


@patch("waifu.views.refresh_serializer_data_urls", side_effect=lambda data: data)
class TestWaifuDetailView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_waifu_detail(self, mock_refresh):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:detail", kwargs={"image_id": "1275631907933261897"}))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json()
        self.assertIn("original_image", data)


def _embedding(first: float, second: float) -> list[float]:
    return [first, second] + [0.0] * 1534


@patch("waifu.views.refresh_serializer_data_urls", side_effect=lambda data: data)
class TestWaifuSimilarImagesView(TestCase):
    def setUp(self):
        self.target = Image.objects.create(
            image_id="target",
            original_image="https://example.com/target.jpg",
            is_nsfw=False,
            embedding=_embedding(1.0, 0.0),
        )
        self.close = Image.objects.create(
            image_id="close",
            original_image="https://example.com/close.jpg",
            is_nsfw=False,
            embedding=_embedding(0.9, 0.1),
        )
        self.far = Image.objects.create(
            image_id="far",
            original_image="https://example.com/far.jpg",
            is_nsfw=False,
            embedding=_embedding(0.0, 1.0),
        )
        self.no_embedding = Image.objects.create(
            image_id="no-embedding",
            original_image="https://example.com/no-embedding.jpg",
            is_nsfw=False,
        )
        self.nsfw = Image.objects.create(
            image_id="nsfw",
            original_image="https://example.com/nsfw.jpg",
            is_nsfw=True,
            embedding=_embedding(0.95, 0.05),
        )

    def test_similar_images_ordered_by_similarity_excludes_target_and_missing_embeddings(self, mock_refresh):
        response = self.client.get(reverse("waifu:similar", kwargs={"image_id": self.target.image_id}))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        results = response.json().get("results")
        image_ids = [item["image_id"] for item in results]

        self.assertNotIn(self.target.image_id, image_ids)
        self.assertNotIn(self.no_embedding.image_id, image_ids)
        self.assertNotIn(self.nsfw.image_id, image_ids)
        self.assertEqual(image_ids[0], self.close.image_id)
        self.assertEqual(image_ids[-1], self.far.image_id)

    def test_similar_images_includes_nsfw_when_requested(self, mock_refresh):
        response = self.client.get(reverse("waifu:similar", kwargs={"image_id": self.target.image_id}), {"nsfw": "1"})
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        image_ids = [item["image_id"] for item in response.json().get("results")]
        self.assertIn(self.nsfw.image_id, image_ids)

    def test_similar_images_returns_404_for_unknown_image_id(self, mock_refresh):
        response = self.client.get(reverse("waifu:similar", kwargs={"image_id": "does-not-exist"}))
        self.assertEqual(response.status_code, 404, "Should return 404 Not Found")

    def test_similar_images_returns_400_when_target_has_no_embedding(self, mock_refresh):
        response = self.client.get(reverse("waifu:similar", kwargs={"image_id": self.no_embedding.image_id}))
        self.assertEqual(response.status_code, 400, "Should return 400 Bad Request")

    def test_similar_images_page_size_is_not_capped(self, mock_refresh):
        response = self.client.get(
            reverse("waifu:similar", kwargs={"image_id": self.target.image_id}), {"count": 100, "nsfw": "1"}
        )
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
        self.assertEqual(len(response.json().get("results")), 3)


@patch("waifu.views.refresh_serializer_data_urls", side_effect=lambda data: data)
class TestRandomWaifuView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_random_waifu(self, mock_refresh):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:random"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json()
        self.assertIn("original_image", data)
