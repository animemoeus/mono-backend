# Generated by Django 4.2.7 on 2024-06-28 06:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("instagram", "0002_alter_user_api_updated_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="api_updated_time",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
