from django.contrib import admin
from django.urls import path, include

from accounts.views import landing, dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("auth/", include("allauth.urls")),
    path("", landing, name="landing"),
    path("dashboard/", dashboard, name="dashboard"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("wallet/", include(("wallet.urls", "wallet"), namespace="wallet")),
    path("courses/", include(("courses.urls", "courses"), namespace="courses")),
    path("activities/", include(("activities.urls", "activities"), namespace="activities")),
    path("ai/", include(("aitutor.urls", "aitutor"), namespace="aitutor")),
]
