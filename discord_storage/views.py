import json

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ChunkedFile, File
from .serializers import (
    BypassDiscordCORSSerializer,
    ChunkedFileSerializer,
    UploadFileFromUrlSerializer,
    UploadFromFileSerializer,
    UploadFromFileV1Serializer,
    UploadFromURLSerializer,
)
from .utils import validate_uuid


def index(request):
    return render(request, "discord_storage/index.html")


@api_view(["POST"])
def upload_from_url(request):
    if request.method == "POST":
        serializer = UploadFileFromUrlSerializer(data=request.data)

        if serializer.is_valid():
            headers = {}

            # for pixiv
            if "pximg.net" in serializer.validated_data["url"]:
                headers["Referer"] = "https://www.pixiv.net/"

            # check if the file URL is valid
            try:
                http_request = requests.head(
                    serializer.validated_data["url"],
                    headers=headers,
                    timeout=3,
                    allow_redirects=True,
                )

                # reject if the http status code is not 200 (OK)
                if http_request.status_code != 200:
                    return Response(
                        {"detail": "Can't get the file from the given URL."},
                        status=http_request.status_code,
                    )

                # check the file size from the given URL
                if http_request.headers.__contains__("Content-Length"):
                    file_size = int(http_request.headers.get("Content-Length")) / 1024

                    # reject if file size is more than 8MB (discord limit)
                    if file_size > 10000:  # 10MB
                        return Response(
                            {"detail": "Can't upload a file larger than 8MB."},
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        )
                else:
                    # reject if the URL does not contain Content-Length headers
                    return Response(
                        {
                            "detail": "Can't process file from given URL because the file size is unknown."
                        },
                        status=status.HTTP_411_LENGTH_REQUIRED,
                    )
            except:
                return Response(
                    {"detail": "Can't get the file from the given URL."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # try to get file from URL
            try:
                http_request = requests.get(
                    serializer.validated_data["url"],
                    headers=headers,
                    stream=True,
                    timeout=5,
                    allow_redirects=True,
                )

                # reject if the http status code is not 200 (OK)
                if http_request.status_code != 200:
                    return Response(
                        {"detail": "Can't get the file from the given URL."},
                        status=http_request.status_code,
                    )

                file = http_request.raw
            except:
                return Response(
                    {"detail": "Can't get the file from the given URL."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # send file to discord cdn server with discord webhook
            discord_webhook = settings.UPLOAD_FROM_URL_WEBHOOK

            files = {serializer.data["filename"]: file}
            response = requests.post(
                discord_webhook,
                files=files,
            )

            if response.status_code == 200:
                data = json.loads(response.text)

                # update File counter in database
                count = File.objects.get_or_create()
                count = count[0]
                count.count += 1
                count.save()

                # remove unused data from dict
                try:
                    del data["attachments"][0]["ephemeral"]
                except:
                    pass

                return Response(data["attachments"][0], status=response.status_code)
            elif response.status_code == 413:
                return Response(
                    {"detail": "File from given URL too large."},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
            else:
                return Response(
                    {"detail": "Unknown error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def upload_from_file(request):
    serializer = UploadFromFileSerializer(data=request.data)

    if serializer.is_valid():
        file = serializer.validated_data["file"]
        file_size = serializer.validated_data["file"].size / 1024

        if file_size > 10000:  # 10MB
            return Response(
                {"detail": "Can't upload a file larger than 8MB."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        else:
            # send file to discord cdn server with discord webhook
            discord_webhook = settings.UPLOAD_FROM_FILE_WEBHOOK

            files = {serializer.validated_data["filename"]: file}
            response = requests.post(
                discord_webhook,
                files=files,
            )

            if response.status_code == 200:
                data = json.loads(response.text)

                # update File counter in database
                count = File.objects.get_or_create()
                count = count[0]
                count.count += 1
                count.save()

                return Response(data["attachments"][0], status=response.status_code)
            elif response.status_code == 413:
                return Response(
                    {"detail": "File from given URL too large."},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
            else:
                return Response(
                    {"detail": "Unknown error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadFromURLView(generics.GenericAPIView):
    serializer_class = UploadFromURLSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        filename = serializer.data.get("filename")
        url = serializer.data.get("url")

        response = requests.get(
            url,
            headers={"Referer": "https://www.pixiv.net/"} if "pximg.net" in url else {},
            stream=True,
            timeout=settings.DISCORD_FILE_SIZE_LIMIT,
            allow_redirects=True,
        )

        if not response.ok:
            return Response(
                {"detail": "Can't get the file from the given URL."},
                status=request.status_code,
            )

        # send file to discord cdn server with discord webhook
        discord_webhook = settings.UPLOAD_FROM_URL_WEBHOOK

        files = {filename: response.raw}
        response = requests.post(
            discord_webhook, files=files, data={"content": filename}
        )

        if response.ok:
            data = json.loads(response.text)

            # update File counter in database
            count = File.objects.get_or_create()
            count = count[0]
            count.count += 1
            count.save()

            _response = data["attachments"][0]
            if _response.get("url"):
                _response["url"] = _response.get("url").split("?")[0]

            if _response.get("proxy_url"):
                _response["proxy_url"] = _response.get("proxy_url").split("?")[0]

            return Response(_response, status=response.status_code)
        elif response.status_code == 413:
            return Response(
                {"detail": "The file retrieved from the provided URL is too large."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        else:
            return Response(
                {"detail": "Unknown error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UploadFromFileView(generics.GenericAPIView):
    serializer_class = UploadFromFileV1Serializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_file = serializer.validated_data["file"]

        # send file to discord cdn server with discord webhook
        discord_webhook = settings.UPLOAD_FROM_FILE_WEBHOOK

        files = {"discord-storage": validated_file}
        response = requests.post(
            discord_webhook,
            files=files,
        )

        if response.ok:
            data = json.loads(response.text)

            # update File counter in database
            count = File.objects.get_or_create()
            count = count[0]
            count.count += 1
            count.save()

            _response = data["attachments"][0]
            if _response.get("url"):
                _response["url"] = _response.get("url").split("?")[0]

            if _response.get("proxy_url"):
                _response["proxy_url"] = _response.get("proxy_url").split("?")[0]

            return Response(_response, status=response.status_code)
        elif response.status_code == 413:
            return Response(
                {"detail": "The file size is too large."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
        else:
            return Response(
                {"detail": "Unknown error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BypassDiscordCORS(generics.GenericAPIView):
    """
    This endpoint will be used as middleware between Discord servers and front-end clients to bypass Discord CORS
    """

    serializer_class = BypassDiscordCORSSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        print(serializer.data.get("url"))

        response = requests.get(serializer.data.get("url"))

        if response.ok:
            return HttpResponse(response.content)
        else:
            return HttpResponse(status=response.status_code)


class ChunkedFiles(generics.GenericAPIView):
    """
    This endpoint will be used as middleware between Discord servers and front-end clients to bypass Discord CORS
    """

    serializer_class = ChunkedFileSerializer

    def get(self, request):
        file_id = request.GET.get("file_id", None)

        if not file_id:
            return Response(
                {"detail": "`file_id` parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not validate_uuid(file_id):
            return Response(
                {"detail": "UUID is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chunked_file = ChunkedFile.objects.filter(uuid=file_id).first()
        if not chunked_file:
            return Response(
                {"detail": f"There is no file with id `{file_id}`"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "file_name": chunked_file.file_name,
                "file_urls": chunked_file.file_urls.split(","),
            }
        )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()

        print(data)

        return Response({"detail": "ヾ(≧ ▽ ≦)ゝ", "data": {"uuid": f"{data.uuid}"}})
