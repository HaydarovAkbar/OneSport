# Generated by Django 4.2.16 on 2024-11-15 16:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chats", "0005_remove_message_attachment_remove_message_is_read_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="attachments",
            field=models.FileField(
                default=datetime.datetime(2024, 11, 15, 16, 14, 25, 180596, tzinfo=datetime.timezone.utc),
                upload_to="media/chat_files/",
            ),
            preserve_default=False,
        ),
    ]
