from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.utils.translation import gettext as _
from .forms import RegisterForm
from .models import User


def landing(request):
    return render(request, "landing.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            referral_code = form.cleaned_data.get("referral_code")
            user = form.save(commit=False)

            # Require email verification before allowing login
            user.is_active = False

            if referral_code:
                try:
                    inviter = User.objects.get(referral_code=referral_code)
                    user.referred_by = inviter
                except User.DoesNotExist:
                    pass

            user.save()

            verify_url = _send_verification_email(request, user)

            # Dev-friendly: if console/file email backend is used, keep the link to show on "sent" page
            backend = getattr(settings, "EMAIL_BACKEND", "") or ""
            if "console" in backend.lower() or "filebased" in backend.lower():
                request.session["last_verify_url"] = verify_url
                request.session["last_verify_email"] = user.email

            return redirect("accounts:verification_sent")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def verification_sent(request):
    ctx = {
        "verify_url": request.session.get("last_verify_url"),
        "verify_email": request.session.get("last_verify_email"),
    }
    return render(request, "accounts/verification_sent.html", ctx)


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, _("Email verified. You can sign in now."))
        return redirect("accounts:login")

    return render(request, "accounts/verification_invalid.html")


def resend_verification(request):
    """Resend verification by email (works even if the user can't log in yet)."""
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        if not email:
            messages.error(request, _("Please enter your email."))
            return redirect("accounts:verification_sent")

        user = User.objects.filter(email__iexact=email).first()
        if user and not user.is_active:
            verify_url = _send_verification_email(request, user)
            backend = getattr(settings, "EMAIL_BACKEND", "") or ""
            if "console" in backend.lower() or "filebased" in backend.lower():
                request.session["last_verify_url"] = verify_url
                request.session["last_verify_email"] = user.email

        # Always respond the same (avoid leaking whether an email exists)
        messages.info(request, _("If an inactive account exists for that email, we sent a verification link."))
        return redirect("accounts:verification_sent")

    return redirect("accounts:verification_sent")

def _send_verification_email(request, user: User) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
    )

    subject = _("✅ Verify your N.O.K account")
    message = (
        _("Hi!") + "\n\n"
        + _("Please verify your email to activate your N.O.K account:") + "\n"
        + f"{verify_url}\n\n"
        + _("If you did not create an account, you can ignore this email.")
    )

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", "")

    if user.email:
        try:
            send_mail(
                subject,
                message,
                from_email,
                [user.email],
                fail_silently=True,  # don't crash prod
            )
        except Exception:
            pass

    return verify_url



@login_required
def dashboard(request):
    user = request.user
    template = {
        "student": "dashboard/student_dashboard.html",
        "teacher": "dashboard/teacher_dashboard.html",
        "ceo": "dashboard/ceo_dashboard.html",
    }.get(user.role, "dashboard/student_dashboard.html")
    return render(request, template)
