from django.core.mail import send_mail
from myhause24.celery import app
from django.template.loader import render_to_string

@app.task
def send_email(email):
    print('task send')
    text = 'Вас приглашают подключиться к системе Demo CRM 24.' \
           'Скачайте приложение:' \
           'Play Market: https://play.google.com/store/apps/details?id=com.avadamedia.program.myhouse24&hl=uk' \
           'App Store: https://itunes.apple.com/us/app/%D0%BC%D0%BE%D0%B9%D0%B4%D0%BE%D0%BC24/id1308075440?l=ru&ls=1&mt=8' \
           'Для дальнейшей информации свяжитесь с администрацией.'
    send_mail('Приглашение в CRM 24', text,
              None,
              [email],
              fail_silently=False
              )
    print('Task completed')


@app.task
def send_new_password_owner(email, password):
    print('task send')
    send_mail(
        'Ваш новый пароль',
        password,
        None,
        [email],
        fail_silently=False
    )
    print('Task completed')
