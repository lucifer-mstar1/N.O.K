from django.contrib import admin
from .models import Activity, ActivityParticipant

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "activity_type", "created_by", "start_at", "entry_fee_z", "prize_pool_z")

@admin.register(ActivityParticipant)
class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = ("activity", "user", "joined_at")
