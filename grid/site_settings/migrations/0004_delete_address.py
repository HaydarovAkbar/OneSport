# Generated by Django 4.2.16 on 2024-11-04 15:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0002_alter_job_location"),
        ("clients", "0002_remove_client_addresses_address"),
        ("recruiters", "0002_alter_bankaccount_account_address_and_more"),
        ("site_settings", "0003_alter_commissionlevel_options_delete_profileimage"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Address",
        ),
    ]
