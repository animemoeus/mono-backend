from django.urls import path

from . import views
from .ninja import api as ninja

urlpatterns = [
    path("", views.index, name="index"),
    path("refresh-url-health-check/", views.refresh_url_health_check, name="refresh-url-health-check"),
    path("refresh/", ninja.urls, name="refresh"),
]


app_name = "discord"
