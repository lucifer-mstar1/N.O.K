from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("verify/sent/", views.verification_sent, name="verification_sent"),
    path("verify/resend/", views.resend_verification, name="resend_verification"),
    path("verify/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=LoginForm),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
