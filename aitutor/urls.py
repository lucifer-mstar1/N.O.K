from django.urls import path
from .views import ai_teacher_chat

app_name = "aitutor"

urlpatterns = [
    path("chat/", ai_teacher_chat, name="chat"),
]
