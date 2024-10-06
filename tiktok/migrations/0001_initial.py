# Generated by Django 4.2.7 on 2023-12-03 14:43

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SavedTiktokVideo",
            fields=[
                ("id", models.CharField(max_length=25, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="TiktokMonitor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False,
                                           verbose_name="ID")),
                ("username", models.CharField(help_text="Should have prefix `@`", max_length=255)),
                ("enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
