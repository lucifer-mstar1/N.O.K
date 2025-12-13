from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Transaction, PaymentOrder, SitePaymentSettings


def teacher_enroll(request):
    """Charge a one-time teacher enrollment fee in Z coins.

    Teachers can buy Z coins via the temporary card flow, convert, then pay this fee.
    """

    if not request.user.is_authenticated or getattr(request.user, "role", "") != "teacher":
        return redirect("accounts:login")

    fee = 10
    pay_settings = SitePaymentSettings.objects.first()
    if pay_settings and pay_settings.teacher_enroll_fee_z:
        fee = int(pay_settings.teacher_enroll_fee_z)

    wallet = request.user.wallet
    if request.method == "POST":
        if request.user.teacher_enrolled:
            messages.info(request, "You are already enrolled.")
            return redirect("dashboard")
        if wallet.z_balance < fee:
            messages.error(request, f"Not enough Z coins. You need {fee} Z coins.")
            return redirect("wallet:wallet")
        wallet.z_balance -= fee
        wallet.save(update_fields=["z_balance"])
        Transaction.objects.create(user=request.user, type="purchase", amount=-fee, description="Teacher enrollment fee")
        request.user.teacher_enrolled = True
        request.user.save(update_fields=["teacher_enrolled"])
        messages.success(request, "Teacher enrollment completed. You can now create courses.")
        return redirect("courses:course_list")

    return render(request, "wallet/teacher_enroll.html", {"fee": fee, "wallet": wallet})
from .services import withdraw_z_to_uzs, handle_first_zcoin_purchase
from django.utils import timezone
from django.shortcuts import get_object_or_404

@login_required
def wallet_view(request):
    wallet = request.user.wallet
    transactions = wallet.transactions.order_by("-created_at")[:50]
    pay_settings = SitePaymentSettings.objects.first()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "deposit":
            amount = Decimal(request.POST.get("amount_uzs", "0") or "0")
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
            else:
                wallet.deposit_uzs(amount)
                Transaction.objects.create(
                    user=request.user,
                    wallet=wallet,
                    type="deposit",
                    amount_uzs=amount,
                    description="Manual deposit (simulate HUMO/Uzcard/Visa)",
                )
                messages.success(request, "Balance topped up (simulation).")
            return redirect("wallet:wallet")

        # MVP payment options:
        # - "demo_gateway": instantly marks the order as paid (for testing only)
        # - "card_request": creates a pending top-up request for manual review/approval
        if action in {"demo_gateway", "card_request"}:
            amount = Decimal(request.POST.get("amount_uzs", "0") or "0")
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
                return redirect("wallet:wallet")

            if action == "demo_gateway":
                order = PaymentOrder.objects.create(
                    user=request.user,
                    provider="card",
                    amount_uzs=amount,
                    status="created",
                    note="Demo payment gateway (simulation)",
                )
                return redirect("wallet:payment_simulate", order_id=order.id)

            # Manual: user sends money to your card and admin approves in Django admin.
            tx_ref = (request.POST.get("tx_ref") or "").strip()
            note = "Manual card transfer request"
            if tx_ref:
                note += f" | TX: {tx_ref}"
            PaymentOrder.objects.create(
                user=request.user,
                provider="card",
                amount_uzs=amount,
                status="created",
                note=note,
            )
            messages.success(
                request,
                "Top-up request created. Please complete the card transfer and wait for admin approval (MVP)."
            )
            return redirect("wallet:wallet")

        if action == "convert":
            uzs_amount = Decimal(request.POST.get("convert_uzs", "0") or "0")
            try:
                z = wallet.convert_uzs_to_z(uzs_amount)
            except ValueError as e:
                messages.error(request, str(e))
            else:
                Transaction.objects.create(
                    user=request.user,
                    wallet=wallet,
                    type="convert_to_z",
                    amount_uzs=-uzs_amount,
                    amount_z=z,
                    description="Converted to Z coins",
                )
                handle_first_zcoin_purchase(request.user, z)
                messages.success(request, f"Converted to {z} Z.")
            return redirect("wallet:wallet")

        if action == "withdraw":
            z_amount = Decimal(request.POST.get("withdraw_z", "0") or "0")
            try:
                net, fee = withdraw_z_to_uzs(request.user, z_amount)
            except ValueError as e:
                messages.error(request, str(e))
            else:
                messages.success(request, f"Withdrew {net} UZS (fee {fee}). (Simulation)")
            return redirect("wallet:wallet")

    return render(request, "wallet/wallet.html", {
        "wallet": wallet,
        "transactions": transactions,
        "pay_settings": pay_settings,
    })


@login_required
def payment_simulate(request, order_id):
    order = get_object_or_404(PaymentOrder, id=order_id, user=request.user)
    if order.status != "created":
        return redirect("wallet:wallet")
    return render(request, "wallet/payment_simulate.html", {"order": order})


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(PaymentOrder, id=order_id, user=request.user)
    if order.status != "paid":
        # mark paid (simulation)
        order.status = "paid"
        order.paid_at = timezone.now()
        order.save()
        wallet = request.user.wallet
        wallet.deposit_uzs(order.amount_uzs)
        Transaction.objects.create(
            user=request.user,
            wallet=wallet,
            type="deposit",
            amount_uzs=order.amount_uzs,
            description=f"Top up via {order.get_provider_display()} (simulation)",
        )
        messages.success(request, "Payment successful! Your wallet was topped up.")
    return redirect("wallet:wallet")
