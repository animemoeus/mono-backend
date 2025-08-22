from django.urls import path

from authentication.views import LoginWithGoogleView

app_name = "authentication"

urlpatterns = [
    path("with-google/", LoginWithGoogleView.as_view(), name="with-google"),
]
