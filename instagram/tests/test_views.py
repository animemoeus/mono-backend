from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from instagram.models import Story, User


# Mock response for request.get calls
class MockResponse:
    def __init__(self):
        self.status_code = 200
        self.content = b"fake-image-content"


class InstagramTestCase(TestCase):
    """Base test class that handles request mocking for all Instagram tests"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level request mocking"""
        # Start request mocker
        cls.request_patcher = patch("requests.get", return_value=MockResponse())
        cls.request_mock = cls.request_patcher.start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level request mocking"""
        cls.request_patcher.stop()
        super().tearDownClass()


class TestInstagramUserHistoryListView(InstagramTestCase):
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


class TestInstagramUserStoryListView(InstagramTestCase):
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


class TestInstagramUserListView(InstagramTestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user with no stories
        self.user_without_stories = User.objects.create(
            username="no_stories_user",
            full_name="No Stories User",
            biography="User with no stories",
            is_private=False,
            is_verified=True,
        )

        # Create a test user with stories
        self.user_with_stories = User.objects.create(
            username="has_stories_user",
            full_name="Has Stories User",
            biography="User with stories",
            is_private=False,
            is_verified=True,
        )

        # Add some stories to the second user
        for i in range(3):
            Story.objects.create(
                user=self.user_with_stories,
                story_id=f"test_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at="2024-05-12T10:00:00Z",
            )

        # Add history to the first user
        self.user_without_stories.biography = "Updated Bio"
        self.user_without_stories.save()

    def test_user_list_contains_new_fields(self):
        """Test that the user list API includes has_stories and has_history fields"""
        url = reverse("instagram:instagram-user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find our test users in the results
        user_without_stories = None
        user_with_stories = None

        for user in data["results"]:
            if user["username"] == "no_stories_user":
                user_without_stories = user
            elif user["username"] == "has_stories_user":
                user_with_stories = user

        # Check that both users were found
        self.assertIsNotNone(user_without_stories, "Test user 'no_stories_user' not found in API response")
        self.assertIsNotNone(user_with_stories, "Test user 'has_stories_user' not found in API response")

        # Check that has_stories field exists and has correct values
        self.assertIn("has_stories", user_without_stories)
        self.assertIn("has_stories", user_with_stories)
        self.assertFalse(user_without_stories["has_stories"])
        self.assertTrue(user_with_stories["has_stories"])

        # Check that has_history field exists and has correct values
        self.assertIn("has_history", user_without_stories)
        self.assertIn("has_history", user_with_stories)
        self.assertTrue(user_without_stories["has_history"])  # This user has history due to biography update
        self.assertTrue(user_with_stories["has_history"])  # All users have at least creation history


class TestInstagramUserDetailView(InstagramTestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user with no stories
        self.user_without_stories = User.objects.create(
            username="detail_no_stories_user",
            full_name="Detail No Stories User",
            biography="User with no stories",
            is_private=False,
            is_verified=True,
        )

        # Create a test user with stories
        self.user_with_stories = User.objects.create(
            username="detail_has_stories_user",
            full_name="Detail Has Stories User",
            biography="User with stories",
            is_private=False,
            is_verified=True,
        )

        # Add some stories to the second user
        for i in range(3):
            Story.objects.create(
                user=self.user_with_stories,
                story_id=f"detail_test_story_{i}",
                thumbnail_url=f"https://example.com/thumbnail_{i}.jpg",
                media_url=f"https://example.com/media_{i}.mp4",
                story_created_at="2024-05-12T10:00:00Z",
            )

        # Add history to the first user
        self.user_without_stories.biography = "Updated Bio"
        self.user_without_stories.save()

    def test_user_detail_contains_new_fields(self):
        """Test that the user detail API includes has_stories and has_history fields"""
        # Test user without stories
        url = reverse("instagram:instagram-user-detail", kwargs={"uuid": self.user_without_stories.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_without_stories = response.json()

        # Check that has_stories field exists and has correct value
        self.assertIn("has_stories", user_without_stories)
        self.assertFalse(user_without_stories["has_stories"])

        # Check that has_history field exists and has correct value
        self.assertIn("has_history", user_without_stories)
        self.assertTrue(user_without_stories["has_history"])  # This user has history due to biography update

        # Test user with stories
        url = reverse("instagram:instagram-user-detail", kwargs={"uuid": self.user_with_stories.uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_with_stories = response.json()

        # Check that has_stories field exists and has correct value
        self.assertIn("has_stories", user_with_stories)
        self.assertTrue(user_with_stories["has_stories"])

        # Check that has_history field exists and has correct value
        self.assertIn("has_history", user_with_stories)
        self.assertTrue(user_with_stories["has_history"])  # All users have at least creation history
