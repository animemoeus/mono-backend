import logging

from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Product
from .tasks import generate_product_embedding_task

logger = logging.getLogger(__name__)


EMBEDDING_ONLY_UPDATE_FIELDS = {"embedding"}


def _enqueue_generate_product_embedding(product_id):
    try:
        generate_product_embedding_task.delay(product_id, True)
    except Exception as exc:
        logger.exception("Failed queueing embedding task for product %s: %s", product_id, exc)


@receiver(post_save, sender=Product)
def trigger_product_embedding_on_save(sender, instance, created, update_fields, **kwargs):
    if update_fields and set(update_fields).issubset(EMBEDDING_ONLY_UPDATE_FIELDS):
        return

    transaction.on_commit(lambda: _enqueue_generate_product_embedding(instance.pk))


@receiver(m2m_changed, sender=Product.tags.through)
def trigger_product_embedding_on_tags_changed(sender, instance, action, **kwargs):
    if action not in {"post_add", "post_remove", "post_clear"}:
        return

    transaction.on_commit(lambda: _enqueue_generate_product_embedding(instance.pk))
