import uuid

import requests
from django.core.files.base import ContentFile


class URLToFileFieldMixin:
    def save_from_url_to_file_field(self, field_name: str, file_extension: str, file_url: str) -> bool:
        """
        Save file from URL to model's FileField.

        Args:
            field_name (str): The name of the FileField
            file_extension (str): File extension (e.g., 'jpg', 'png')
            file_url (str): URL of the file to download

        Returns:
            bool: True if file was saved successfully, False otherwise

        Raises:
            AttributeError: If field_name doesn't exist in model
        """
        REQUEST_TIMEOUT = 30

        if not hasattr(self, field_name):
            raise AttributeError(f"Field '{field_name}' does not exist")

        try:
            response = requests.get(file_url, timeout=REQUEST_TIMEOUT)
            if not response.ok:
                return False

            getattr(self, field_name).save(f"{uuid.uuid4()}.{file_extension}", ContentFile(response.content))
            return True

        except requests.RequestException:
            return False
