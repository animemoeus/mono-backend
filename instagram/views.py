import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework import filters
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RoastingLog
from .models import User as InstagramUser
from .models import UserFollower as InstagramUserFollower
from .models import UserFollowing as InstagramUserFollowing
from .pagination import InstagramUserFollowerPagination, InstagramUserFollowingPagination, InstagramUserListPagination
from .serializers import (
    InstagramUserDetailSerializer,
    InstagramUserFollowerSerializer,
    InstagramUserFollowingSerializer,
    InstagramUserListSerializer,
)
from .utils import InstagramAPI, RoastingIG


class InstagramUserListView(ListAPIView):
    queryset = InstagramUser.objects.all()
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


class InstagramUserDetailView(RetrieveAPIView):
    serializer_class = InstagramUserDetailSerializer
    queryset = InstagramUser.objects.all()
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
