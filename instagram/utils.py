import logging

import boto3
from botocore.client import Config
from django.conf import settings

logger = logging.getLogger(__name__)


def user_profile_picture_upload_location(instance, filename):
    return f"instagram/user/{instance.username}/profile-picture/{filename}"


def user_stories_upload_location(instance, filename):
    return f"instagram/user/{instance.user.username}/stories/{filename}"


def user_follower_profile_picture_upload_location(instance, filename):
    return f"instagram/user-follower/{instance.username}/profile-picture/{filename}"


def user_following_profile_picture_upload_location(instance, filename):
    return f"instagram/user-following/{instance.username}/profile-picture/{filename}"


def get_s3_signed_url(file_key: str, expiration: int = 3600) -> str | None:
    """
    Generate a URL for accessing files, handling both S3 and local storage.

    Args:
        file_key: The key/path of the file relative to MEDIA_ROOT
        expiration: URL expiration time in seconds (default: 1 hour), only used for S3

    Returns:
        URL string for accessing the file
        For S3: A signed URL that expires
        For local: A media URL that uses WhiteNoise
        None if there's an error
    """
    # Check if we're using S3 storage in production
    try:
        using_s3 = all(
            (
                getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""),
                getattr(settings, "AWS_S3_ENDPOINT_URL", ""),
                getattr(settings, "AWS_S3_ACCESS_KEY_ID", ""),
                getattr(settings, "AWS_S3_SECRET_ACCESS_KEY", ""),
            )
        )
    except Exception as e:
        logger.debug(f"S3 settings not configured: {str(e)}")
        using_s3 = False

    print("================using s3:", using_s3)

    if using_s3:
        try:
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
            )

            url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": file_key},
                ExpiresIn=expiration,
            )
            return url
        except Exception as e:
            logger.error(f"Error generating signed URL for {file_key}: {str(e)}")
            return None
    else:
        # In local development, use the media URL
        try:
            return f"{settings.MEDIA_URL.rstrip('/')}/{file_key.lstrip('/')}"
        except Exception as e:
            logger.error(f"Error generating media URL for {file_key}: {str(e)}")
            return None
