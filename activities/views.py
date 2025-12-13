from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Activity, ActivityParticipant
from wallet.models import Transaction

@login_required
def activity_list(request):
    activities = Activity.objects.all().order_by("start_at")
    return render(request, "activities/activity_list.html", {"activities": activities})

@login_required
def join_activity(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    user = request.user
    if request.method == "POST":
        if ActivityParticipant.objects.filter(activity=activity, user=user).exists():
            messages.info(request, "You are already in this event.")
            return redirect("activities:activity_list")

        fee = activity.entry_fee_z
        if fee > 0:
            wallet = user.wallet
            if wallet.balance_z < fee:
                messages.error(request, "Not enough Z coins to join this event.")
                return redirect("activities:activity_list")
            wallet.spend_z(fee)
            Transaction.objects.create(
                user=user,
                wallet=wallet,
                type="tournament_fee",
                amount_z=-fee,
                description=f"Joined {activity.title}",
            )
        ActivityParticipant.objects.create(activity=activity, user=user)
        messages.success(request, "Welcome to the event! Show your best and learn with others.")
        return redirect("activities:activity_list")
    return redirect("activities:activity_list")
