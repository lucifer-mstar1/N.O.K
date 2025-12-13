from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


def _limited_role_choices(request):
    """Only superusers can assign the CEO role."""
    base = [("student", "Student"), ("teacher", "Teacher"), ("ceo", "CEO")]
    if request.user.is_superuser:
        return base
    return [("student", "Student"), ("teacher", "Teacher")]

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("NOK fields", {"fields": ("role", "display_name", "referral_code", "referred_by", "xp", "streak_days")}),
    )
    list_display = ("username", "display_name", "role", "email", "referral_code", "referred_by", "xp", "streak_days")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Hide CEO option for non-superusers.
        if "role" in form.base_fields:
            form.base_fields["role"].choices = _limited_role_choices(request)
        return form

    def save_model(self, request, obj, form, change):
        # Enforce CEO creation policy.
        if obj.role == "ceo":
            if not request.user.is_superuser:
                obj.role = "teacher"  # fallback
            # CEO is NOT an admin; keep admin powers off.
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)
