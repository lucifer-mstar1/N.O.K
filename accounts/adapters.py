from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return reverse("dashboard")

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # VERY IMPORTANT: call parent method so email is actually sent
        super().send_confirmation_mail(request, emailconfirmation, signup)
