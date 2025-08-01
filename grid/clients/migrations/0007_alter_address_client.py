# Generated by Django 4.2.16 on 2024-11-06 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0006_alter_client_linkedin_company_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="addresses",
                to="clients.client",
            ),
        ),
    ]
