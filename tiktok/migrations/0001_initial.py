# Generated by Django 4.2.16 on 2025-02-16 06:41

from django.db import migrations, models
import django.db.models.deletion
import tiktok.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TiktokMonitor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(help_text="Should have prefix `@`", max_length=255)),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "uuid",
                    models.CharField(
                        default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False
                    ),
                ),
                ("username", models.CharField(max_length=255, unique=True)),
                ("nickname", models.CharField(max_length=255)),
                ("user_id", models.CharField(max_length=255, unique=True)),
                ("followers", models.PositiveIntegerField(default=0)),
                ("following", models.PositiveIntegerField(default=0)),
                ("visible_content_count", models.PositiveIntegerField(default=0)),
                ("avatar_url", models.URLField(max_length=555)),
                (
                    "avatar_file",
                    models.ImageField(
                        blank=True, null=True, upload_to=tiktok.models.tiktok_profile_picture_upload_location
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="SavedTiktokVideo",
            fields=[
                ("id", models.CharField(max_length=25, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tiktok_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to="tiktok.tiktokmonitor"
                    ),
                ),
            ],
        ),
    ]
