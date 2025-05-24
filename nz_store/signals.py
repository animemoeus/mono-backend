import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AccountStock

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AccountStock)
def sync_product_stock_on_account_save(sender, instance, **kwargs):
    """Sync product stock when an account stock is created or updated"""
    try:
        instance.product.sync_stock_with_accounts()
    except Exception as e:
        logger.error(f"Failed to sync stock for product {instance.product.id}: {e}")


@receiver(post_delete, sender=AccountStock)
def sync_product_stock_on_account_delete(sender, instance, **kwargs):
    """Sync product stock when an account stock is deleted"""
    try:
        instance.product.sync_stock_with_accounts()
    except Exception as e:
        logger.error(f"Failed to sync stock for product {instance.product.id} after deletion: {e}")
