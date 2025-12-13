from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("wallet", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("payme", "Payme"), ("click", "Click"), ("card", "Card")], max_length=20)),
                ("amount_uzs", models.DecimalField(decimal_places=2, max_digits=18)),
                ("status", models.CharField(choices=[("created", "Created"), ("paid", "Paid"), ("failed", "Failed"), ("canceled", "Canceled")], default="created", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("external_id", models.CharField(blank=True, max_length=64, null=True)),
                ("note", models.CharField(blank=True, max_length=255, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_orders", to=settings.AUTH_USER_MODEL)),
            ],
        )
    ]
