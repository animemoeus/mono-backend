from django.db import models
from solo.models import SingletonModel


class Setting(SingletonModel):
    class Meta:
        verbose_name = "Rent AI Setting"

    data_source_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
