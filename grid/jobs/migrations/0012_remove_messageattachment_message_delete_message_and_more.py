# Generated by Django 4.2.16 on 2024-11-11 21:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0011_remove_stagelog_candidate_remove_stagelog_from_stage_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="messageattachment",
            name="message",
        ),
        migrations.DeleteModel(
            name="Message",
        ),
        migrations.DeleteModel(
            name="MessageAttachment",
        ),
    ]
