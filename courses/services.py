from decimal import Decimal
from wallet.models import Transaction
from .models import Enrollment
from django.db import transaction as db_transaction
from wallet.models import ZCOIN_RATE_UZS

PLATFORM_COMMISSION = Decimal("0.10")  # 10%
ENROLL_XP_REWARD = 50  # xp for buying a part

def purchase_course_part(student, part):
    if student.role != "student":
        raise ValueError("Only students can purchase course parts")

    student_wallet = student.wallet
    teacher = part.course.teacher
    teacher_wallet = teacher.wallet

    price_z = part.price_z
    # UX improvement: if student doesn't have enough Z, auto-convert from UZS when possible.
    if student_wallet.balance_z < price_z:
        needed_z = price_z - student_wallet.balance_z
        needed_uzs = (needed_z * ZCOIN_RATE_UZS).quantize(Decimal("0.01"))
        if student_wallet.balance_uzs < needed_uzs:
            raise ValueError("Not enough funds. Top up your wallet or buy more Z.")
        # Convert only the required amount.
        converted_z = student_wallet.convert_uzs_to_z(needed_uzs)
        Transaction.objects.create(
            user=student,
            wallet=student_wallet,
            type="convert_to_z",
            amount_uzs=-needed_uzs,
            amount_z=converted_z,
            description=f"Auto-convert to complete purchase for {part}",
        )

    commission_z = (price_z * PLATFORM_COMMISSION).quantize(Decimal("0.01"))
    teacher_z = price_z - commission_z

    with db_transaction.atomic():
        student_wallet.spend_z(price_z)
        Transaction.objects.create(
            user=student,
            wallet=student_wallet,
            type="course_purchase",
            amount_z=-price_z,
            description=f"Purchase {part}",
        )

        teacher_wallet.credit_z(teacher_z)
        Transaction.objects.create(
            user=teacher,
            wallet=teacher_wallet,
            type="course_purchase",
            amount_z=teacher_z,
            description=f"Earned from {student.username} for {part}",
        )

        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            part=part,
            defaults={"is_trial": False, "progress_percent": 0},
        )

        # reward XP for commitment
        from accounts.models import User  # local import
        student.xp += ENROLL_XP_REWARD
        student.save()

    return enrollment
