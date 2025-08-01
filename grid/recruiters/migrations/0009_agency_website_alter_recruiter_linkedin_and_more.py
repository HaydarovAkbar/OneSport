# Generated by Django 4.2.16 on 2024-11-07 14:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recruiters", "0008_merge_20241106_2214"),
    ]

    operations = [
        migrations.AddField(
            model_name="agency",
            name="website",
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="recruiter",
            name="linkedin",
            field=models.URLField(default="https://www.google.com", max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="recruiter",
            name="status",
            field=models.SmallIntegerField(
                choices=[
                    (0, "Active"),
                    (1, "Pending Approval"),
                    (2, "Pending Signup"),
                    (3, "Wait list"),
                    (4, "Rejected"),
                ],
                default=2,
            ),
        ),
    ]
