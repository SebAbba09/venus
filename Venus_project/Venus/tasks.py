# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Reminder, Notification
from django.utils import timezone

@shared_task
def send_event_reminders():
    notifications = Notification.objects.filter(notified=False, notify_at__lte=timezone.now())
    for notification in notifications:
        send_mail(
            'Rappel d\'événement',
            f'Rappel pour votre événement : {notification.event.title}',
            'from@example.com',
            ['user@example.com'],
            fail_silently=False,
        )
        notification.notified = True
        notification.save()