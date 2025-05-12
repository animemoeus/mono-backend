from django.urls import path

from .views import (
    InstagramStoryDetailView,
    InstagramStoryListView,
    InstagramUserDetailView,
    InstagramUserFollowerListView,
    InstagramUserFollowingListView,
    InstagramUserHistoryListView,
    InstagramUserListView,
    InstagramUserStoryListView,
    RoastingProfileView,
)

urlpatterns = [
    path("users/", InstagramUserListView.as_view(), name="instagram_user_list"),
    path(
        "users/<str:uuid>/",
        InstagramUserDetailView.as_view(),
        name="instagram-user-detail",
    ),
    path(
        "users/<str:uuid>/history/",
        InstagramUserHistoryListView.as_view(),
        name="instagram-user-history-list",
    ),
    path(
        "users/<str:uuid>/stories/",
        InstagramUserStoryListView.as_view(),
        name="instagram-user-story-list",
    ),
    path(
        "users/<str:username>/follower/",
        InstagramUserFollowerListView.as_view(),
        name="instagram-user-follower-list",
    ),
    path(
        "users/<str:username>/following/",
        InstagramUserFollowingListView.as_view(),
        name="instagram-user-following-list",
    ),
    path("roasting/<str:username>/", RoastingProfileView.as_view(), name="roasting"),
    path("stories/", InstagramStoryListView.as_view(), name="instagram-story-list"),
    path(
        "stories/<str:story_id>/",
        InstagramStoryDetailView.as_view(),
        name="instagram-story-detail",
    ),
]

app_name = "instagram"
