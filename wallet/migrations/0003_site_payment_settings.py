from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0002_paymentorder"),
    ]

    operations = [
        migrations.CreateModel(
            name="SitePaymentSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("card_last4", models.CharField(blank=True, max_length=4)),
                ("card_holder", models.CharField(blank=True, max_length=120)),
                ("telegram_support", models.CharField(blank=True, max_length=120)),
                ("teacher_enroll_fee_z", models.PositiveIntegerField(default=10)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Site payment settings",
                "verbose_name_plural": "Site payment settings",
            },
        ),
    ]
