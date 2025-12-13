from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User

class RegisterForm(UserCreationForm):
    # CEO accounts must NOT be self-registered.
    role = forms.ChoiceField(choices=[("student", _("Student")), ("teacher", _("Teacher"))])
    referral_code = forms.CharField(required=False)

    # Teacher-only fields
    teacher_subject = forms.CharField(required=False, max_length=120, label=_('What will you teach?'))
    teacher_pack_price_z = forms.IntegerField(required=False, min_value=0, label=_('Price per lesson pack (Z coins)'))
    teacher_bio = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label=_('Short bio'))

    def clean_role(self):
        role = self.cleaned_data.get("role")
        if role == "ceo":
            raise ValidationError(_("CEO accounts can only be created by an administrator."))
        return role

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        if role == "teacher":
            if not (cleaned.get("teacher_subject") or "").strip():
                self.add_error("teacher_subject", _("Please enter what you will teach."))
            if cleaned.get("teacher_pack_price_z") is None:
                self.add_error("teacher_pack_price_z", _("Please set your lesson pack price."))
        return cleaned

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "email",
            "role",
            "referral_code",
            "teacher_subject",
            "teacher_pack_price_z",
            "teacher_bio",
            "password1",
            "password2",
        ]


class LoginForm(AuthenticationForm):
    """Shows a clear message when account is inactive (email not verified)."""
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                _("Please verify your email first. Open the verification link we sent you."),
                code='inactive',
            )
        return super().confirm_login_allowed(user)
