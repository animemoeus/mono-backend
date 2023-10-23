from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("upload-from-url/", views.upload_from_url),
    path("upload-from-file/", views.upload_from_file),
    path(
        "api/upload-from-url/",
        views.UploadFromURLView.as_view(),
        name="upload-from-url",
    ),
    path(
        "api/upload-from-file/",
        views.UploadFromFileView.as_view(),
        name="upload-from-file",
    ),
]
