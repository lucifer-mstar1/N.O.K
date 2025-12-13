from django.contrib import admin
from decimal import Decimal

from .models import Wallet, Transaction, PaymentOrder, SitePaymentSettings, ZCOIN_RATE_UZS

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_uzs", "balance_z")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # Transaction model stores Z-coin delta in `amount_z`
    list_display = ("user", "type", "amount_uzs", "amount_z", "created_at")
    list_filter = ("type", "created_at")


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    # PaymentOrder stores UZS amount; we also show an *estimated* Z-coin amount for convenience.
    list_display = ("id", "user", "z_amount", "amount_uzs", "provider", "status", "created_at")
    list_filter = ("provider", "status", "created_at")
    search_fields = ("user__username", "user__email")

    @admin.display(description="Z amount", ordering="amount_uzs")
    def z_amount(self, obj: PaymentOrder):
        if not obj.amount_uzs:
            return 0
        try:
            return (Decimal(obj.amount_uzs) / Decimal(ZCOIN_RATE_UZS)).quantize(Decimal("0.01"))
        except Exception:
            return 0


@admin.register(SitePaymentSettings)
class SitePaymentSettingsAdmin(admin.ModelAdmin):
    # SitePaymentSettings fields: card_holder_name, card_last4, telegram_support, teacher_enrollment_fee_z, updated_at
    list_display = ("id", "card_holder_name", "card_last4", "telegram_support", "teacher_enrollment_fee_z", "updated_at")
