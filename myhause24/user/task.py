from django.core.mail import send_mail
from myhause24.celery import app


@app.task
def send_email_for_verify(message, email):
    print('task send')
    send_mail('Регистрация в CRM 24',
              message,
              None,
              [email],
              fail_silently=False
              )
    print('Task completed')



