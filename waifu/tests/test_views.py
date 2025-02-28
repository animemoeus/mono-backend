import requests
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


class TestWaifuListView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_waifu_list(self):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:index"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json().get("results")[0]
        response = requests.get(data.get("original_image"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")


class TestWaifuDetailView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_waifu_detail(self):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:detail", kwargs={"image_id": "1275631907933261897"}))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json()
        response = requests.get(data.get("original_image"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")


class TestRandomWaifuView(TestCase):
    def setUp(self):
        create_waifu_init_data()

    def test_get_random_waifu(self):
        self.assertEqual(Image.objects.all().count(), 2)
        response = self.client.get(reverse("waifu:random"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")

        data = response.json()
        response = requests.get(data.get("original_image"))
        self.assertEqual(response.status_code, 200, "Should return 200 OK")
