# Generated by Django 4.2.16 on 2024-11-06 17:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recruiters", "0006_merge_20241106_1719"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recruiter",
            name="status",
            field=models.SmallIntegerField(
                choices=[(0, "Active"), (1, "Pending Approval"), (2, "Wait list"), (3, "Rejected")], default=1
            ),
        ),
        migrations.AlterField(
            model_name="recruiter",
            name="user",
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
    ]
