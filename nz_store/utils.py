from uuid import uuid4


def get_product_image_upload_path(instance, filename):
    """Generate a unique upload path for product images."""
    uuid = uuid4()
    return f"products/{uuid}/{filename}"
