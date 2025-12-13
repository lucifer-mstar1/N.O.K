from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

ACTIVITY_TYPES = [
    ("tournament", "Tournament"),
    ("standup", "Stand-up"),
    ("meeting", "Meeting"),
    ("hackathon", "Hackathon"),
]

class Activity(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_activities")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    entry_fee_z = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prize_pool_z = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title} ({self.activity_type})"

class ActivityParticipant(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("activity", "user")

    def __str__(self):
        return f"{self.user} -> {self.activity}"
