# Generated by Django 4.2.16 on 2024-11-11 22:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0010_alter_client_logo"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="primary",
            field=models.BooleanField(default=False),
        ),
    ]
