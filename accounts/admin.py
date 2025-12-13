from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
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

    # ---- Permissions rules ----
    def has_add_permission(self, request):
        # CEOs cannot create users (prevents CEO creating another CEO).
        if getattr(request.user, "role", "") == "ceo" and not request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # CEOs cannot delete users at all.
        if getattr(request.user, "role", "") == "ceo" and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj=obj)

    def save_model(self, request, obj, form, change):
        is_actor_ceo = getattr(request.user, "role", "") == "ceo" and not request.user.is_superuser

        # 1) CEOs cannot edit CEO accounts at all
        if is_actor_ceo and change and getattr(obj, "role", "") == "ceo":
            raise PermissionDenied("CEOs cannot edit other CEO accounts.")

        # 2) Only superuser can assign/keep CEO role
        if obj.role == "ceo" and not request.user.is_superuser:
            # If non-superuser tries to set CEO, block it hard
            raise PermissionDenied("Only superusers can assign the CEO role.")

        # 3) If user is CEO, allow admin access but no superuser powers
        if obj.role == "ceo":
            obj.is_staff = True          # allow /admin/
            obj.is_superuser = False     # prevent full power

        super().save_model(request, obj, form, change)
