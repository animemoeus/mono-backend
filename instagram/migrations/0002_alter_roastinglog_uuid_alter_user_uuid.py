# Generated by Django 4.2.16 on 2025-02-10 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("instagram", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roastinglog",
            name="uuid",
            field=models.CharField(default="6ffdb7e0-d50a-465c-bd11-652842130db2", editable=False, max_length=36),
        ),
        migrations.AlterField(
            model_name="user",
            name="uuid",
            field=models.CharField(default="915a31d4-fcde-4e67-9594-3d23fcb30b5e", editable=False, max_length=36),
        ),
    ]
