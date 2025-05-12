from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from instagram.models import Story, User


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


class TestInstagramUserStoryListView(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create(
            username="test_user",
            full_name="Test User",
            biography="Test Bio",
            is_private=False,
            is_verified=True,
        )

        # Create some test stories
        self.stories = []
        for i in range(3):
            story = Story.objects.create(
                user=self.user,
                story_id=f"test_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at="2024-05-12T10:00:00Z",
            )
            self.stories.append(story)

    def test_get_user_stories_success(self):
        """Test successful retrieval of user stories"""
        url = reverse("instagram:instagram-user-story-list", kwargs={"uuid": self.user.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check pagination fields
        self.assertIn("count", data)
        self.assertIn("results", data)

        # We should have 3 stories
        self.assertEqual(len(data["results"]), 3)

        # Check the story record fields
        story_record = data["results"][0]
        self.assertIn("story_id", story_record)
        self.assertIn("thumbnail", story_record)
        self.assertIn("media", story_record)
        self.assertIn("created_at", story_record)
        self.assertIn("story_created_at", story_record)

    def test_get_user_stories_nonexistent_user(self):
        """Test attempting to get stories for a non-existent user"""
        import uuid

        url = reverse("instagram:instagram-user-story-list", kwargs={"uuid": uuid.uuid4()})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stories_ordering(self):
        """Test that stories are properly ordered by story_created_at"""
        # Create stories with different creation dates
        Story.objects.all().delete()
        dates = ["2024-05-12T10:00:00Z", "2024-05-12T11:00:00Z", "2024-05-12T12:00:00Z"]

        for i, date in enumerate(dates):
            Story.objects.create(
                user=self.user,
                story_id=f"ordered_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at=date,
            )

        url = reverse("instagram:instagram-user-story-list", kwargs={"uuid": self.user.uuid})

        # Test default ordering (newest first)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify descending order
        story_dates = [story["story_created_at"] for story in data]
        self.assertEqual(story_dates, sorted(story_dates, reverse=True))

        # Test ascending order
        response = self.client.get(f"{url}?ordering=story_created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify ascending order
        story_dates = [story["story_created_at"] for story in data]
        self.assertEqual(story_dates, sorted(story_dates))

    def test_pagination(self):
        """Test pagination of user stories"""
        Story.objects.all().delete()
        # Create more stories (InstagramUserStoryPagination.page_size is 10)
        for i in range(15):
            Story.objects.create(
                user=self.user,
                story_id=f"paginated_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at="2024-05-12T10:00:00Z",
            )

        url = reverse("instagram:instagram-user-story-list", kwargs={"uuid": self.user.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify pagination data
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        # Verify page size
        self.assertEqual(len(data["results"]), 10)  # Default page size

        # Test with custom page size
        response = self.client.get(f"{url}?count=5")
        data = response.json()
        self.assertEqual(len(data["results"]), 5)
