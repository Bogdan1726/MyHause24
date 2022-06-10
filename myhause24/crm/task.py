from django.core.mail import send_mail
from myhause24.celery import app
from django.template.loader import render_to_string

@app.task
def send_email(email):
    print('task send')
    text = 'Вас приглашают подключиться к системе CRM 24.\n' \
           'Скачайте приложение:\n' \
           '\n' \
           'Play Market: https://play.google.com/store/apps/details?id=com.avadamedia.program.myhouse24&hl=uk\n' \
           'App Store: https://itunes.apple.com/us/app/%D0%BC%D0%BE%D0%B9%D0%B4%D0%BE%D0%BC24/id1308075440?l=ru&ls=1&mt=8\n' \
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
        'CRM 24 Administrations',
        f'Ваш новый пароль - {password}',
        None,
        [email],
        fail_silently=False
    )
    print('Task completed')


@app.task
def send_invite_user(email, role):
    print('task send')
    text = f'Вас приглашают подключиться к системе CRM 24 с уровнем доступа: {role}.\n' \
           f'\n' \
           f'Ваш логин:{email}\n' \
           f'Чтобы узнать пароль свяжитесь с администрацией.\n' \
           f'\n' \
           f'Ссылка для входа: http://myhouse24.avada-media.ua/admin/'
    send_mail('Приглашение в CRM 24', text,
              None,
              [email],
              fail_silently=False
              )
    print('Task completed')