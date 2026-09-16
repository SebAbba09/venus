# venus/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='connexion'),

    path('test/', views.test_view, name='test_view'),
    path('contact/', views.contact, name='contact'),
    path('accueil/', views.accueil, name='accueil'),
    path('mdp/', views.mdp, name='mdp'),
    path('connexion/', views.connexion, name='connexion'),
    path('login/', views.login, name='login'),
    path('avatar_gallery/', views.avatar_gallery, name='avatar_gallery'),
    path('merci/', views.merci, name='merci'),

    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('change-password/', views.password_change_view, name='password_change'),
    path('change-password/done/', views.password_change_done_view, name='password_change_done'),



    path('translate/', views.translate, name='translate'),


    path('add_event/', views.add_event, name='add_event'),
    path('api/events/update/<int:event_id>/', views.update_event, name='update_event'),
    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('even_list/', views.event_list, name='event_list'),



    path('home/', views.home, name='home'),

    path('chat_view/', views.chat_view, name='chat'),
    path('chat_form/', views.chat_form, name='chat_form'),
    path('chat_poll/', views.chat_poll, name='chat_poll'),




    path('chat_with_context/', views.chat_view_with_context, name='chat_view_with_context'),



    path('personalized_chat_with_sentiment/', views.personalized_chat_with_sentiment_view, name='personalized_chat_with_sentiment_view'),
]
