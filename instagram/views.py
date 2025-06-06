import requests
from django.conf import settings
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RoastingLog, Story
from .models import User as InstagramUser
from .models import UserFollower as InstagramUserFollower
from .models import UserFollowing as InstagramUserFollowing
from .pagination import (
    InstagramUserFollowerPagination,
    InstagramUserFollowingPagination,
    InstagramUserHistoryPagination,
    InstagramUserListPagination,
    InstagramUserStoryPagination,
)
from .serializers import (
    InstagramStorySerializer,
    InstagramUserDetailSerializer,
    InstagramUserFollowerSerializer,
    InstagramUserFollowingSerializer,
    InstagramUserHistorySerializer,
    InstagramUserListSerializer,
)
from .utils import InstagramAPI, RoastingIG


class InstagramUserListView(ListAPIView):
    queryset = InstagramUser.objects.prefetch_related("story_set").all()
    serializer_class = InstagramUserListSerializer
    pagination_class = InstagramUserListPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "full_name", "biography"]
    ordering_fields = [
        "created_at",
        "updated_at",
        "username",
        "full_name",
    ]
    ordering = ["-created_at"]


class InstagramStoryListView(ListAPIView):
    """
    View for listing all stories across all users, with optional filtering and ordering
    """

    serializer_class = InstagramStorySerializer
    pagination_class = InstagramUserStoryPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = {
        "user__username": ["exact"],
    }
    ordering_fields = ["story_created_at", "created_at"]
    ordering = ["-story_created_at"]

    def get_queryset(self):
        return Story.objects.select_related("user").all()


class InstagramStoryDetailView(RetrieveAPIView):
    """
    View for retrieving details of a specific story
    """

    serializer_class = InstagramStorySerializer
    queryset = Story.objects.all()
    lookup_field = "story_id"


class InstagramUserDetailView(RetrieveAPIView):
    serializer_class = InstagramUserDetailSerializer
    queryset = InstagramUser.objects.prefetch_related("story_set").all()
    lookup_field = "uuid"


class InstagramUserFollowerListView(ListAPIView):
    serializer_class = InstagramUserFollowerSerializer
    pagination_class = InstagramUserFollowerPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["username"]
    ordering = ["username"]

    def get_queryset(self):
        username = self.kwargs.get("username", None)
        queryset = InstagramUserFollower.objects.filter(user__username=username)

        if not queryset:
            raise NotFound
        return queryset


class InstagramUserFollowingListView(ListAPIView):
    serializer_class = InstagramUserFollowingSerializer
    pagination_class = InstagramUserFollowingPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["username"]
    ordering = ["-username"]

    def get_queryset(self):
        username = self.kwargs.get("username", None)
        queryset = InstagramUserFollowing.objects.filter(user__username=username)

        if not queryset:
            raise NotFound
        return queryset


class InstagramUserHistoryListView(ListAPIView):
    serializer_class = InstagramUserHistorySerializer
    pagination_class = InstagramUserHistoryPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "history_date",
    ]
    ordering = ["-history_date"]

    def get_queryset(self):
        uuid = self.kwargs.get("uuid", None)

        try:
            user = InstagramUser.objects.get(uuid=uuid)
            queryset = user.history.all()

            if not queryset.exists():
                raise NotFound("No history records found for this user")

            return queryset
        except InstagramUser.DoesNotExist:
            raise NotFound("Instagram user not found")


class InstagramUserStoryListView(ListAPIView):
    serializer_class = InstagramStorySerializer
    pagination_class = InstagramUserStoryPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["story_created_at", "created_at"]
    ordering = ["-story_created_at"]

    def get_queryset(self):
        uuid = self.kwargs.get("uuid", None)
        try:
            user = InstagramUser.objects.get(uuid=uuid)
            queryset = Story.objects.select_related("user").filter(user=user)
            return queryset
        except InstagramUser.DoesNotExist:
            raise NotFound("Instagram user not found")
        except Exception as e:
            raise NotFound(f"An error occurred while fetching stories: {e}")


class RoastingProfileView(APIView):
    def get(self, request, username: str):
        captcha = request.query_params.get("captcha")
        if not self.recaptcha_validation(captcha):
            return Response(
                {"error": "Hmm, kayaknya captchanya salah deh... coba cek lagi deh~"},
                status=400,
            )

        try:
            instagram_api = InstagramAPI()

            user_info = cache.get(f"roastig_{username}")
            if not user_info:
                user_info = instagram_api.get_user_info_v2(username)
                if user_info:
                    cache.set(f"roastig_{username}", user_info, timeout=1800)
        except Exception as e:
            _ = e
            return Response(
                {
                    "error": "Duh, nggak bisa dapetin info dari server Instagram nih, jaringan internetnya jelek bgt kek muka lu. Coba lu klik lagi tombolnya."
                },
                status=404,
            )

        try:
            roasting_text = RoastingIG.get_instagram_roasting_text(user_info)
            user_info["roasting_text"] = roasting_text
        except Exception as e:
            _ = e
            return Response(
                {
                    "error": "Jaringan internetnya jelek bgt anjir, kek mukalu. Coba cuci muka dulu terus klik tombolnya lagi."
                },
                status=500,
            )

        # Save to database
        RoastingLog.objects.create(username=username, roasting_text=roasting_text, user_data=user_info)
        return Response(user_info)

    def recaptcha_validation(self, captcha) -> bool:
        if settings.DEBUG and captcha == "ARTERTENDEAN":
            return True

        url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {"secret": settings.GOOGLE_CAPTCHA_SECRET_KEY, "response": captcha}

        response = requests.request("POST", url, data=payload)

        return response.json().get("success", False)
