from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from instagram.models import Story, User


class TestInstagramStoryListView(TestCase):
    """Tests for the Instagram story list view."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create(
            username="test_user1",
            full_name="Test User 1",
            biography="Test Bio 1",
            is_private=False,
            is_verified=True,
        )
        self.user2 = User.objects.create(
            username="test_user2",
            full_name="Test User 2",
            biography="Test Bio 2",
            is_private=False,
            is_verified=False,
        )

        # Create stories for each user
        self.stories = []
        for i in range(3):
            # User 1 stories
            story1 = Story.objects.create(
                user=self.user1,
                story_id=f"user1_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_user1_{i}.jpg",
                media_url=f"https://example.com/media_user1_{i}.mp4",
                story_created_at=f"2024-05-12T10:00:0{i}Z",
            )
            self.stories.append(story1)

            # User 2 stories
            story2 = Story.objects.create(
                user=self.user2,
                story_id=f"user2_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_user2_{i}.jpg",
                media_url=f"https://example.com/media_user2_{i}.mp4",
                story_created_at=f"2024-05-12T11:00:0{i}Z",
            )
            self.stories.append(story2)

    def test_get_all_stories_success(self):
        """Test successful retrieval of all stories."""
        url = reverse("instagram:instagram-story-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check pagination fields
        self.assertIn("count", data)
        self.assertIn("results", data)

        # We should have 6 stories in total
        self.assertEqual(data["count"], 6)

        # The default page size is 10, so all stories should be in the results
        self.assertEqual(len(data["results"]), 6)

        # Check the story record fields
        story_record = data["results"][0]
        self.assertIn("story_id", story_record)
        self.assertIn("thumbnail", story_record)
        self.assertIn("media", story_record)
        self.assertIn("created_at", story_record)
        self.assertIn("story_created_at", story_record)
        self.assertIn("user", story_record)

        # Verify user details are included
        self.assertIn("username", story_record["user"])
        self.assertIn("full_name", story_record["user"])

    def test_stories_ordering(self):
        """Test that stories are properly ordered by story_created_at."""
        url = reverse("instagram:instagram-story-list")

        # Test default ordering (newest first)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify descending order (newest first)
        story_dates = [story["story_created_at"] for story in data]
        self.assertEqual(story_dates, sorted(story_dates, reverse=True))

        # Test ascending order
        response = self.client.get(f"{url}?ordering=story_created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()["results"]

        # Verify ascending order (oldest first)
        story_dates = [story["story_created_at"] for story in data]
        self.assertEqual(story_dates, sorted(story_dates))

        # Test ordering by created_at
        response = self.client.get(f"{url}?ordering=created_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination(self):
        """Test pagination of stories."""
        # Delete existing stories and create more for testing pagination
        Story.objects.all().delete()

        # Create 15 stories (InstagramUserStoryPagination.page_size is 10)
        for i in range(15):
            # Format dates properly with hours between 10-12 based on index
            hour = 10 + (i // 5)
            Story.objects.create(
                user=self.user1,
                story_id=f"paginated_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at=f"2024-05-12T{hour}:00:00Z",
            )

        url = reverse("instagram:instagram-story-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify pagination data
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)

        # Verify total count
        self.assertEqual(data["count"], 15)

        # Verify page size (default is 10)
        self.assertEqual(len(data["results"]), 10)

        # Verify next page URL exists
        self.assertIsNotNone(data["next"])

        # Test with custom page size
        response = self.client.get(f"{url}?count=5")
        data = response.json()
        self.assertEqual(len(data["results"]), 5)

        # Navigate to next page
        response = self.client.get(f"{url}?page=2")
        data = response.json()
        self.assertEqual(len(data["results"]), 5)  # 15 total, 10 on first page, 5 on second
        self.assertIsNone(data["next"])
        self.assertIsNotNone(data["previous"])
