import logging

from celery import shared_task

from .models import Product

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def generate_product_embedding_task(product_id: int, force: bool = True):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        logger.warning("Product %s not found for embedding task.", product_id)
        return f"Product {product_id} not found"

    product.generate_embedding(force=force)
    return f"Embedding generated for product {product_id}"


@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def generate_product_embeddings_task(product_ids: list[int], force: bool = True):
    success_count = 0
    fail_count = 0

    for product_id in product_ids:
        try:
            generate_product_embedding_task(product_id, force)
            success_count += 1
        except Exception:
            fail_count += 1
            logger.exception("Failed generating embedding for product %s in batch task.", product_id)

    return f"Embedding batch done. Success: {success_count}, Failed: {fail_count}"
