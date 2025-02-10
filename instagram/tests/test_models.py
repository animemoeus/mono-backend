from django.test import TestCase

from instagram.models import Story as InstagramStory
from instagram.models import User as InstagramUser
from instagram.models import UserFollowing


class InstagramTestCase(TestCase):
    databases = {"default", "tidb"}

    def setUp(self):
        self.user_1 = InstagramUser.objects.create(username="arter_tendean")
        self.user_2 = InstagramUser.objects.create(username="retra_naednet")
        self.user_3 = InstagramUser.objects.create(username="sydnaei")
        self.follower_1 = InstagramUser.objects.create(username="follower_1")
        self.following_1 = InstagramUser.objects.create(username="following_1")

    def test_get_information_from_api(self):
        user_1_info = self.user_1.get_information_from_api()

        self.assertEqual(self.user_1.instagram_id, None, "Instagram user id should be empty")
        self.user_1.update_information_from_api()
        self.assertEqual(
            self.user_1.instagram_id,
            user_1_info.get("pk"),
            "Instagram user id should be available",
        )

        self.assertEqual(
            user_1_info.get("username"),
            "arter_tendean",
            'Username should be "arter_tendean"',
        )

        self.user_1.update_information_from_api()
        self.assertIsNotNone(
            self.user_1.profile_picture,
            "After update information from API, profile picture should not be None",
        )

        self.assertEqual(
            self.user_1.full_name,
            user_1_info["full_name"],
            "User full_name should equal with the data in the API response",
        )
        self.assertEqual(
            self.user_1.biography,
            user_1_info["biography"],
            "User biography should equal with the data in the API response",
        )
        self.assertEqual(
            self.user_1.follower_count,
            user_1_info["follower_count"],
            "User follower_count should equal with the data in the API response",
        )
        self.assertEqual(
            self.user_1.following_count,
            user_1_info["following_count"],
            "User following_count should equal with the data in the API response",
        )

        with self.assertRaises(Exception) as context:
            self.user_2.get_information_from_api()
        self.assertEqual(str(context.exception), "Cannot get user information from Instagram API")

    def test_get_user_stories(self):
        user_1_stories = self.user_1.get_user_stories()

        self.assertEqual(type(user_1_stories), list)

    def test_update_user_following(self):
        UserFollowing.objects.create(user=self.user_1, username="following_1")
        UserFollowing.objects.create(user=self.user_1, username="following_2")
        UserFollowing.objects.create(user=self.user_1, username="following_3")
        UserFollowing.objects.create(user=self.user_2, username="following_3")

        print(UserFollowing.objects.filter(user=self.user_1))
        print(UserFollowing.objects.all())
        UserFollowing.objects.filter(user=self.user_1).delete()
        print(UserFollowing.objects.all())
        self.user_1.update_user_following()
        for i in UserFollowing.objects.filter(user=self.user_1):
            print(i.__dict__)

        # self.user_1.update_user_following()


class TestInstagramUserStory(TestCase):
    databases = {"default", "tidb"}

    def setUp(self):
        self.user_1 = InstagramUser.objects.create(username="arter_tendean")

    def test_save_user_stories(self):
        stories_data = [
            {
                "story_id": "3404466952080125061",
                "thumbnail_url": "https://scontent-dfw5-1.cdninstagram.com/v/t51.2885-15/449721680_1485652635376429_4422997268457196089_n.jpg?stp=dst-jpg_e15&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi42NDB4MTEzNi5zZHIuZjcxODc4In0&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=101&_nc_ohc=Py_tXCqmBE4Q7kNvgFMGIBz&edm=AA0lj5EBAAAA&ccb=7-5&ig_cache_key=MzQwNDQ2Njk1MjA4MDEyNTA2MQ%3D%3D.2-ccb7-5&oh=00_AYCZ4rHvdd3P2ftEOYHAEbBp3Zw3tq9UGqbxnt91INXjxg&oe=668C0943&_nc_sid=0a490e",
                "media_url": "https://scontent-dfw5-2.cdninstagram.com/o1/v/t16/f1/m78/E24044B1FF8F515EF760C0E8EF583799_video_dashinit.mp4?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLnN0b3J5LmMyLjcyMC5iYXNlbGluZSJ9&_nc_ht=scontent-dfw5-2.cdninstagram.com&_nc_cat=102&vs=1202423404005280_3665450179&_nc_vs=HBksFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyL0UyNDA0NEIxRkY4RjUxNUVGNzYwQzBFOEVGNTgzNzk5X3ZpZGVvX2Rhc2hpbml0Lm1wNBUAAsgBABUCGDpwYXNzdGhyb3VnaF9ldmVyc3RvcmUvR0lHWW5nSmxVOVF4SHJZR0FKU0ZQZjZ4d1JBcWJwUjFBQUFGFQICyAEAKAAYABsBiAd1c2Vfb2lsATEVAAAm4IXb2Z6K%2B0AVAigCQzMsF0AuAAAAAAAAGBJkYXNoX2Jhc2VsaW5lXzFfdjERAHXoBwA%3D&_nc_rid=3a57774c9c&ccb=9-4&oh=00_AYDm7sO5AsZ_T-eaTYkX5bZesgTikO86ignWQ8ebMBhfkg&oe=6687F41E&_nc_sid=0a490e",
                "created_at": "2024-07-04T03:34:57+00:00",
            },
            {
                "story_id": "3404470715477878910",
                "thumbnail_url": "https://scontent-dfw5-1.cdninstagram.com/v/t51.2885-15/449852317_522918156730685_6808092323485416645_n.jpg?stp=dst-jpg_e15&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi42NDB4MTEzNi5zZHIuZjcxODc4In0&_nc_ht=scontent-dfw5-1.cdninstagram.com&_nc_cat=105&_nc_ohc=Juc4HQIwdPcQ7kNvgHBA69c&edm=AA0lj5EBAAAA&ccb=7-5&ig_cache_key=MzQwNDQ3MDcxNTQ3Nzg3ODkxMA%3D%3D.2-ccb7-5&oh=00_AYDvzuaslZlrz5uTNKkGDFss9MD56dj5Zh8hDRH9jyqEug&oe=668C0BCF&_nc_sid=0a490e",
                "media_url": "https://scontent-dfw5-2.cdninstagram.com/o1/v/t16/f2/m69/An992Gu7Ybi3MozLbmd1U7Z_OS7RcjgE1-UvPLFs_8uIajKMJdLBTSZTGjcvWm-GkOmcs9iD9jloywll9-0-maB9.mp4?efg=eyJ2ZW5jb2RlX3RhZyI6InZ0c192b2RfdXJsZ2VuLnN0b3J5LmMyLjEwODAuYmFzZWxpbmUifQ&_nc_ht=scontent-dfw5-2.cdninstagram.com&_nc_cat=108&vs=1471594203489024_386723967&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HTzhYTVFmNVktNThMUUlEQUJORlhLS1hzZUFOYnBSMUFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dFTEM2Z0tBcG4tbjZ0d1pBTHlEd0otdDFJRk5icFIxQUFBRhUCAsgBACgAGAAbAYgHdXNlX29pbAExFQAAJtSV%2B9%2Fz841BFQIoAkMzLBdALe6XjU%2FfOxgWZGFzaF9iYXNlbGluZV8xMDgwcF92MREAdegHAA%3D%3D&_nc_rid=3a57738fe1&ccb=9-4&oh=00_AYDr2_y0jR8Fek5c4CIZ3PlhUx_n__7mV9umrw5PJ17rfA&oe=66881522&_nc_sid=0a490e",
                "created_at": "2024-07-04T03:42:15+00:00",
            },
        ]

        for story in stories_data:
            InstagramStory.objects.create(
                user=self.user_1,
                story_id=story["story_id"],
                thumbnail_url=story["thumbnail_url"],
                media_url=story["media_url"],
                story_created_at=story["created_at"],
            )

        self.assertEqual(
            InstagramStory.objects.count(),
            len(stories_data),
            "The number of stories should be equal to the number of stories data",
        )

        for story in InstagramStory.objects.all():
            self.assertEqual(story.user, self.user_1, "The user should be the same")
            self.assertIsNotNone(story.story_id, "The story_id should not be None")
            self.assertIsNotNone(story.thumbnail_url, "The thumbnail_url should not be None")
            self.assertIsNotNone(story.media_url, "The media_url should not be None")
            self.assertIsNotNone(story.story_created_at, "The story_created_at should not be None")
            self.assertIsNotNone(story.thumbnail, "The thumbnail should not be None")
            self.assertIsNotNone(story.media, "The media should not be None")
