from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator
from .task import send_email_for_verify
from myhause24.settings import ALLOWED_HOSTS


def send_email_for_verification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://127.0.0.1:8000'
    context = {
        'domain': host,
        'user': user,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user)
    }
    message = render_to_string(
        'user/pages/template_mail_for_activate.html',
        context=context
    )
    send_email_for_verify.delay(message, user.email)
