from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("<int:pk>/", views.course_detail, name="course_detail"),
    path("buy/<int:part_id>/", views.buy_part, name="buy_part"),
    path("<int:course_id>/review/", views.add_review, name="add_review"),
]
