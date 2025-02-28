# Generated by Django 4.2.16 on 2025-02-28 08:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("instagram", "0012_alter_userfollower_profile_picture"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalUser",
            fields=[
                ("uuid", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("instagram_id", models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ("username", models.CharField(db_index=True, max_length=150)),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("profile_picture", models.TextField(blank=True, max_length=100, null=True)),
                (
                    "profile_picture_url",
                    models.URLField(help_text="The original profile picture URL from Instagram", max_length=500),
                ),
                ("biography", models.TextField(blank=True)),
                ("follower_count", models.PositiveIntegerField(default=0)),
                ("following_count", models.PositiveIntegerField(default=0)),
                (
                    "updated_from_api_datetime",
                    models.DateTimeField(blank=True, null=True, verbose_name="Update from API datetime"),
                ),
                ("allow_auto_update_stories", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical user",
                "verbose_name_plural": "historical users",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
