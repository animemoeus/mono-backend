from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import AccountStock


@receiver(post_save, sender=AccountStock)
def sync_product_stock_on_account_save(sender, instance, **kwargs):
    """Sync product stock when an account stock is created or updated"""
    instance.product.sync_stock_with_accounts()


@receiver(post_delete, sender=AccountStock)
def sync_product_stock_on_account_delete(sender, instance, **kwargs):
    """Sync product stock when an account stock is deleted"""
    instance.product.sync_stock_with_accounts()
