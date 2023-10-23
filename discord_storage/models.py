import uuid

from django.db import models


class File(models.Model):
    count = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total files: {self.count}"


class ChunkedFile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(blank=True, null=True)
    file_urls = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uuid} — {self.file_name}"
