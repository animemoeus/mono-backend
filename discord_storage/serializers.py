import requests
from django.conf import settings
from rest_framework import serializers

from .models import ChunkedFile


class UploadFileFromUrlSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=100)
    url = serializers.CharField(max_length=500)


class UploadFromFileSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=100)
    file = serializers.FileField(max_length=255)


class UploadFromURLSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=100)
    url = serializers.URLField(max_length=500)

    def validate_url(self, value):
        headers = {"Referer": "https://www.pixiv.net/"} if "pximg.net" in value else {}

        response = requests.head(
            value,
            headers=headers,
            timeout=3,
            allow_redirects=True,
        )

        if not response.ok:
            raise serializers.ValidationError("Can't get the file from the given URL.")

        # check the file size from the given URL
        if response.headers.__contains__("Content-Length"):
            file_size = int(response.headers.get("Content-Length")) / 1024

            # reject if file size is more than 25MB (discord limit)
            if file_size > settings.DISCORD_FILE_SIZE_LIMIT * 1024:
                raise serializers.ValidationError(
                    f"The file size should not exceed {settings.DISCORD_FILE_SIZE_LIMIT} megabytes."
                )
        else:
            raise serializers.ValidationError(
                "Can't process file from given URL because the file size is unknown."
            )

        return value


class UploadFromFileV1Serializer(serializers.Serializer):
    file = serializers.FileField(max_length=255)

    def validate_file(self, file):
        max_size = settings.DISCORD_FILE_SIZE_LIMIT * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                f"The file size should not exceed {settings.DISCORD_FILE_SIZE_LIMIT} megabytes."
            )

        return file


class BypassDiscordCORSSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)

    def validate_url(self, url):
        if "cdn.discordapp.com" not in url and "media.discordapp.net" not in url:
            raise serializers.ValidationError("Invalid URL")

        return url


class ChunkedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChunkedFile
        fields = ("file_name", "file_size", "file_urls")

    def create(self, validated_data):
        return ChunkedFile.objects.create(**validated_data)
