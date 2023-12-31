# Generated by Django 4.2.6 on 2023-10-22 09:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("discord_storage", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChunkedFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("file_name", models.CharField(max_length=255)),
                ("file_size", models.IntegerField(blank=True, null=True)),
                ("file_urls", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
