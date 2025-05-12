from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from instagram.models import User

# class TestRoastingProfileView(TestCase):
#     def setUp(self):
#         self.instagram_username = "angiehsl"

#     @override_settings(DEBUG=True)
#     def test_get_roasting(self):
#         response = self.client.get(
#             f"/instagram/roasting/{self.instagram_username}/?captcha=ARTERTENDEAN"
#         ).json()
#         print(response.get("roasting_text"))
#         self.assertIsNotNone(response.get("roasting_text"))


class TestInstagramUserHistoryListView(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            username="test_user",
            full_name="Test User",
            biography="Test Bio",
            is_private=False,
            is_verified=True,
            media_count=10,
            follower_count=100,
            following_count=50,
        )

        # Save some history by updating the user
        self.user.biography = "Updated Bio"
        self.user.save()
        self.user.follower_count = 200
        self.user.save()

    def test_get_user_history_success(self):
        """Test successful retrieval of user history"""
        url = reverse("instagram:instagram-user-history-list", kwargs={"uuid": self.user.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check pagination fields
        self.assertIn("count", data)
        self.assertIn("results", data)

        # We should have at least 3 history records (creation + 2 updates)
        self.assertTrue(len(data["results"]) >= 3)

        # Check the history record fields
        history_record = data["results"][0]
        self.assertIn("uuid", history_record)
        self.assertIn("username", history_record)
        self.assertIn("full_name", history_record)
        self.assertIn("biography", history_record)
        self.assertIn("follower_count", history_record)
        self.assertIn("history_date", history_record)

    def test_get_user_history_nonexistent_user(self):
        """Test attempting to get history for a non-existent user"""
        import uuid

        url = reverse("instagram:instagram-user-history-list", kwargs={"uuid": uuid.uuid4()})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_ordering(self):
        """Test that history is properly ordered by history_date"""
        url = reverse("instagram:instagram-user-history-list", kwargs={"uuid": self.user.uuid})

        # Test default ordering (newest first)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify descending order
        dates = [record["history_date"] for record in data]
        self.assertEqual(dates, sorted(dates, reverse=True))

        # Test ascending order
        response = self.client.get(f"{url}?ordering=history_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify ascending order
        dates = [record["history_date"] for record in data]
        self.assertEqual(dates, sorted(dates))

    def test_pagination(self):
        """Test pagination of user history"""
        # Create more history records
        for i in range(20):  # InstagramUserHistoryPagination.page_size is 15
            self.user.follower_count += 1
            self.user.save()

        url = reverse("instagram:instagram-user-history-list", kwargs={"uuid": self.user.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify pagination data
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        # Verify page size
        self.assertEqual(len(data["results"]), 15)  # Default page size

        # Test with custom page size
        response = self.client.get(f"{url}?count=5")
        data = response.json()
        self.assertEqual(len(data["results"]), 5)
