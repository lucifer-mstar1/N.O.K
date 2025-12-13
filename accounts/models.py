from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("ceo", "CEO"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    display_name = models.CharField(max_length=100, blank=True)

    # Teacher profile (captured during teacher signup)
    teacher_subject = models.CharField(max_length=120, blank=True)
    teacher_pack_price_z = models.PositiveIntegerField(default=0)
    teacher_bio = models.TextField(blank=True)
    teacher_enrolled = models.BooleanField(default=False)

    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.SET_NULL, related_name="referrals"
    )

    xp = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.username
        if not self.referral_code:
            self.referral_code = (
                self.username[:3].upper()
                + "".join(random.choices(string.digits, k=5))
            )
        super().save(*args, **kwargs)

    def level(self) -> int:
        # simple gamified level: sqrt(xp / 10) rounded
        from math import sqrt
        return int(sqrt(self.xp / 10)) if self.xp > 0 else 1

    def __str__(self):
        return f"{self.display_name} ({self.role})"
