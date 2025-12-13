from django.db import models
from django.conf import settings
from decimal import Decimal

User = settings.AUTH_USER_MODEL

ZCOIN_RATE_UZS = Decimal("10000")   # 1 Z = 10 000 so'm
REFERRAL_BONUS_RATE = Decimal("0.05")  # 5% of z purchase as bonus

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance_uzs = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_z = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} wallet"

    def deposit_uzs(self, amount):
        self.balance_uzs += Decimal(amount)
        self.save()

    def convert_uzs_to_z(self, uzs_amount):
        uzs_amount = Decimal(uzs_amount)
        if uzs_amount > self.balance_uzs:
            raise ValueError("Not enough UZS")
        z_amount = uzs_amount / ZCOIN_RATE_UZS
        self.balance_uzs -= uzs_amount
        self.balance_z += z_amount
        self.save()
        return z_amount

    def spend_z(self, z_amount):
        z_amount = Decimal(z_amount)
        if z_amount > self.balance_z:
            raise ValueError("Not enough Z coins")
        self.balance_z -= z_amount
        self.save()

    def credit_z(self, z_amount):
        self.balance_z += Decimal(z_amount)
        self.save()

TRANSACTION_TYPES = [
    ("deposit", "Deposit UZS"),
    ("convert_to_z", "Convert to Z coins"),
    ("course_purchase", "Course purchase"),
    ("tournament_fee", "Tournament fee"),
    ("prize", "Prize"),
    ("withdraw", "Withdraw"),
    ("referral_bonus", "Referral bonus"),
]

PAYMENT_PROVIDERS = [
    ("payme", "Payme"),
    ("click", "Click"),
    ("card", "Card"),
]

PAYMENT_STATUSES = [
    ("created", "Created"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("canceled", "Canceled"),
]


class PaymentOrder(models.Model):
    """Simple payment order model.

    This project ships with a *simulation* flow so you can plug real providers
    (Payme/Click) later without rewriting the wallet.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_orders")
    provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDERS)
    amount_uzs = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    external_id = models.CharField(max_length=64, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.provider} {self.amount_uzs} ({self.status})"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount_uzs = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    amount_z = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.user} - {self.created_at:%Y-%m-%d}"


class SitePaymentSettings(models.Model):
    """Singleton-like settings editable in Django admin.

    Used for the temporary "manual card" payment flow and support links.
    """

    card_holder_name = models.CharField(max_length=120, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    telegram_support = models.CharField(max_length=120, blank=True, help_text="e.g. @nok_support")

    teacher_enrollment_fee_z = models.PositiveIntegerField(default=10)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Payment Settings"
