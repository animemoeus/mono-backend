from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User as InstagramUser
from .models import UserFollower as InstagramUserFollower
from .models import UserFollowing as InstagramUserFollowing


class InstagramUserListSerializer(ModelSerializer):
    class Meta:
        model = InstagramUser
        exclude = ["profile_picture_url"]


class InstagramUserDetailSerializer(ModelSerializer):
    class Meta:
        model = InstagramUser
        exclude = [
            "profile_picture_url",
        ]


class InstagramUserFollowerSerializer(ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUserFollower
        exclude = ["profile_picture_url", "user"]

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return obj.profile_picture_url

        return obj.profile_picture.url


class InstagramUserFollowingSerializer(ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = InstagramUserFollowing
        exclude = ["profile_picture_url", "user"]

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return obj.profile_picture_url

        return obj.profile_picture.url


class InstagramUserHistorySerializer(ModelSerializer):
    """
    Serializer for historical records of Instagram User profiles.
    """

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
