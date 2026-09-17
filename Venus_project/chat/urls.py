from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.conversation_view, name="conversation"),
    path("api/messages/", views.message_view, name="message"),
]
