# Generated by Django 4.2.16 on 2024-11-04 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import grid.recruiters.models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("site_settings", "0003_alter_commissionlevel_options_delete_profileimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="Agency",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("agency_name", models.CharField(blank=True, max_length=255, null=True)),
                ("make_payable_to", models.CharField(max_length=255)),
                ("linkedin", models.CharField(blank=True, max_length=255, null=True)),
                ("is_individual", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["agency_name"],
            },
        ),
        migrations.CreateModel(
            name="JobCategory",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("name", models.CharField(max_length=255)),
                ("icon_name", models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="TaxInformation",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("ein", models.CharField(blank=True, max_length=50, null=True)),
                ("tin", models.CharField(blank=True, max_length=50, null=True)),
                ("business_number", models.CharField(blank=True, max_length=50, null=True)),
                ("sin", models.CharField(blank=True, max_length=50, null=True)),
                ("vat", models.CharField(blank=True, max_length=50, null=True)),
                ("utr", models.CharField(blank=True, max_length=50, null=True)),
                ("abn", models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Recruiter",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("introduction", models.TextField(blank=True, null=True)),
                ("story", models.TextField(blank=True, null=True)),
                ("approval_date", models.DateTimeField(blank=True, null=True)),
                ("commission_share", models.SmallIntegerField(blank=True, null=True)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Active"),
                            (1, "Pending Approval"),
                            (2, "Email Verification Pending"),
                            (3, "Email Verified"),
                            (4, "Wait list"),
                            (5, "Rejected"),
                        ],
                        default=2,
                    ),
                ),
                ("stripe_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "profile_photo",
                    models.ImageField(
                        upload_to="profile_photos/", validators=[grid.recruiters.models.validate_image_size]
                    ),
                ),
                ("linkedin", models.CharField(blank=True, max_length=255, null=True)),
                ("superuser", models.BooleanField(default=False)),
                (
                    "address",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="site_settings.address"
                    ),
                ),
                (
                    "agency",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="recruiters.agency"
                    ),
                ),
                (
                    "primary_industry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="primary_recruiters",
                        to="recruiters.jobcategory",
                    ),
                ),
                (
                    "sec_industry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="secondary_recruiters",
                        to="recruiters.jobcategory",
                    ),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="BankAccount",
            fields=[
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="created")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("account_name", models.CharField(max_length=255)),
                ("account_number", models.CharField(max_length=50)),
                ("routing_number", models.CharField(blank=True, max_length=50, null=True)),
                ("institution_number", models.CharField(blank=True, max_length=50, null=True)),
                ("transit_number", models.CharField(blank=True, max_length=50, null=True)),
                ("sort_code", models.CharField(blank=True, max_length=50, null=True)),
                ("bsb_code", models.CharField(blank=True, max_length=50, null=True)),
                ("bank_name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "account_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="account_addresses",
                        to="site_settings.address",
                    ),
                ),
                (
                    "bank_address",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bank_accounts",
                        to="site_settings.address",
                    ),
                ),
            ],
            options={
                "ordering": ["account_name"],
            },
        ),
        migrations.AddField(
            model_name="agency",
            name="bank_details",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="recruiters.bankaccount"
            ),
        ),
        migrations.AddField(
            model_name="agency",
            name="tax_details",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="recruiters.taxinformation"
            ),
        ),
    ]
