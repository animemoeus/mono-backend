from django.urls import path

from . import views

app_name = "cinematch"

urlpatterns = [
    path(
        "recommendations/",
        views.MovieRecommendationAPIView.as_view(),
        name="movie-recommendations",
    ),
]
