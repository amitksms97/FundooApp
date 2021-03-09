from django.core.mail import EmailMessage
from celery import shared_task


class Utils:
    @shared_task
    def send_reminder_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()
