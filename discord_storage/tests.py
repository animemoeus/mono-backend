from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class UploadFromURLViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_upload_from_url(self):
        url = "https://cdn.discordapp.com/attachments/858938620425404426/1015080280995934358/waifu-animemoeus.webp"
        filename = "waifu.png"
        data = {"filename": filename, "url": url}

        response = self.client.post(
            "/discord-storage/api/upload-from-url/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UploadFromFileViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_upload_from_file(self):
        # Create a dummy file
        file_content = b"fake binary data"
        uploaded_file = SimpleUploadedFile("fakefile.txt", file_content)

        data = {"file": uploaded_file}

        response = self.client.post(
            "/discord-storage/api/upload-from-file/", data, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
