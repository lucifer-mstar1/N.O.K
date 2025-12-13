from decimal import Decimal
from .models import ZCOIN_RATE_UZS, Transaction, REFERRAL_BONUS_RATE

WITHDRAW_FEE = Decimal("0.01")  # 1%

def withdraw_z_to_uzs(user, z_amount):
    wallet = user.wallet
    z_amount = Decimal(z_amount)

    if z_amount > wallet.balance_z:
        raise ValueError("Not enough Z coins")

    gross_uzs = z_amount * ZCOIN_RATE_UZS
    fee_uzs = (gross_uzs * WITHDRAW_FEE).quantize(Decimal("0.01"))
    net_uzs = gross_uzs - fee_uzs

    wallet.balance_z -= z_amount
    wallet.save()

    Transaction.objects.create(
        user=user,
        wallet=wallet,
        type="withdraw",
        amount_z=-z_amount,
        amount_uzs=-net_uzs,
        description=f"Withdraw {net_uzs} UZS, fee {fee_uzs}",
    )

    return net_uzs, fee_uzs

def handle_first_zcoin_purchase(user, z_amount):
    if user.referred_by:
        inviter = user.referred_by
        inviter_wallet = inviter.wallet
        bonus = (z_amount * REFERRAL_BONUS_RATE).quantize(Decimal("0.01"))
        inviter_wallet.credit_z(bonus)
        Transaction.objects.create(
            user=inviter,
            wallet=inviter_wallet,
            type="referral_bonus",
            amount_z=bonus,
            description=f"Referral bonus from {user.username}",
        )
