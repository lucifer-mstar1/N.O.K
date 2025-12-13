from django.urls import path
from . import views

app_name = "wallet"

urlpatterns = [
    path("", views.wallet_view, name="wallet"),
    path("teacher-enroll/", views.teacher_enroll, name="teacher_enroll"),
    path("pay/<int:order_id>/", views.payment_simulate, name="payment_simulate"),
    path("pay/<int:order_id>/success/", views.payment_success, name="payment_success"),
]
