from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Story as InstagramStory
from .models import User as InstagramUser
from .models import UserFollower as InstagramUserFollower
from .models import UserFollowing as InstagramUserFollowing
from .utils import get_s3_signed_url


class InstagramUserListSerializer(ModelSerializer):
    has_stories = serializers.SerializerMethodField()
    has_history = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUser
        exclude = ["profile_picture_url"]

    def get_has_stories(self, obj):
        # Check if story_set is prefetched before making the query
        if hasattr(obj, "_prefetched_objects_cache") and "story_set" in obj._prefetched_objects_cache:
            # Use the prefetched data
            return bool(obj._prefetched_objects_cache["story_set"])
        else:
            # Fallback to query if not prefetched
            return obj.story_set.exists()

    def get_has_history(self, obj):
        # Check if history is prefetched before making the query
        if hasattr(obj, "_prefetched_objects_cache") and "history" in obj._prefetched_objects_cache:
            # Use the prefetched data
            return bool(obj._prefetched_objects_cache["history"])
        else:
            # Fallback to query if not prefetched
            return obj.history.exists()


class InstagramUserDetailSerializer(ModelSerializer):
    has_stories = serializers.SerializerMethodField()
    has_history = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUser
        exclude = [
            "profile_picture_url",
        ]

    def get_has_stories(self, obj):
        # Check if story_set is prefetched before making the query
        if hasattr(obj, "_prefetched_objects_cache") and "story_set" in obj._prefetched_objects_cache:
            # Use the prefetched data
            return bool(obj._prefetched_objects_cache["story_set"])
        else:
            # Fallback to query if not prefetched
            return obj.story_set.exists()

    def get_has_history(self, obj):
        # Check if history is prefetched before making the query
        if hasattr(obj, "_prefetched_objects_cache") and "history" in obj._prefetched_objects_cache:
            # Use the prefetched data
            return bool(obj._prefetched_objects_cache["history"])
        else:
            # Fallback to query if not prefetched
            return obj.history.exists()


class InstagramUserFollowerSerializer(ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUserFollower
        exclude = ["profile_picture_url", "user"]

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return obj.profile_picture_url

        file_key = obj.profile_picture.name
        signed_url = get_s3_signed_url(file_key)
        if signed_url:
            return signed_url

        if file_key.startswith("media/"):
            file_key = file_key[6:]
        return f"{settings.MEDIA_URL.rstrip('/')}/{file_key.lstrip('/')}"


class InstagramUserFollowingSerializer(ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUserFollowing
        exclude = ["profile_picture_url", "user"]

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return obj.profile_picture_url

        file_key = obj.profile_picture.name
        signed_url = get_s3_signed_url(file_key)
        if signed_url:
            return signed_url

        if file_key.startswith("media/"):
            file_key = file_key[6:]
        return f"{settings.MEDIA_URL.rstrip('/')}/{file_key.lstrip('/')}"


class InstagramUserHistorySerializer(ModelSerializer):
    """
    Serializer for historical records of Instagram User profiles.
    """

    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUser.history.model
        exclude = [
            # Fields added by simple_history
            "history_user",
            "history_change_reason",
            "history_type",
            # Original model fields
            "profile_picture_url",
        ]

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return obj.profile_picture_url

        # For historical records, profile_picture might be just a path string
        file_key = (
            obj.profile_picture.lstrip("/") if isinstance(obj.profile_picture, str) else obj.profile_picture.name
        )

        # Try to get a signed URL if using S3
        signed_url = get_s3_signed_url(file_key)
        if signed_url:
            return signed_url

        # For local storage, construct the full URL
        # Remove 'media/' prefix if present since it's already in MEDIA_URL
        if file_key.startswith("media/"):
            file_key = file_key[6:]
        return f"{settings.MEDIA_URL.rstrip('/')}/{file_key.lstrip('/')}"


class InstagramStorySerializer(ModelSerializer):
    user = InstagramUserDetailSerializer(read_only=True)

    class Meta:
        model = InstagramStory
        exclude = ["thumbnail_url", "media_url"]
