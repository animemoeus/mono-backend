# Generated by Django 4.2.16 on 2025-05-12 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instagram", "0013_historicaluser"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicaluser",
            name="updated_from_api_datetime",
        ),
        migrations.RemoveField(
            model_name="user",
            name="updated_from_api_datetime",
        ),
        migrations.AddField(
            model_name="historicaluser",
            name="is_private",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicaluser",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicaluser",
            name="media_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="historicaluser",
            name="updated_at_from_api",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Updated From API"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_private",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="media_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="updated_at_from_api",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Updated From API"),
        ),
    ]
