from django.contrib import admin
from solo.admin import SingletonModelAdmin
from unfold.admin import ModelAdmin

from .models import Setting


@admin.register(Setting)
class SettingAdmin(SingletonModelAdmin, ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
