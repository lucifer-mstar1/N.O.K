from django.urls import path
from . import views

app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="activity_list"),
    path("<int:activity_id>/join/", views.join_activity, name="join_activity"),
]
