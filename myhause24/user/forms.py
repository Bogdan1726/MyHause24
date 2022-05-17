from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.db.models import Q
from .models import User
from django.utils.translation import gettext_lazy as _
from snowpenguin.django.recaptcha3.fields import ReCaptchaField


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Email',
                                      'class': 'form-control'}))

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password',
                                          'placeholder': 'Пароль',
                                          'class': 'form-control'}),
    )
    remember_me = forms.BooleanField(required=False, initial=True,
                                     widget=forms.CheckboxInput(
                                         attrs={'class': 'form-check-input',
                                                'id': 'checkbox1'}
                                     ))

    remember_me2 = forms.BooleanField(required=False, initial=True,
                                      widget=forms.CheckboxInput(
                                          attrs={'class': 'form-check-input',
                                                 'id': 'checkbox2'}
                                      ))

    captcha = ReCaptchaField()

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        remember_me = self.cleaned_data.get('remember_me')
        remember_me2 = self.cleaned_data.get('remember_me2')
        print(self.cleaned_data.get('captcha'))

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
            if '/admin/' in self.request.POST['redirect']:
                try:
                    User.objects.get(email=username, is_staff=True)
                    if not remember_me2:
                        self.request.session.set_expiry(0)
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()
            if '/cabinet/' in self.request.POST['redirect']:
                try:
                    User.objects.get(
                        Q(email=username) | Q(user_id=username), is_staff=False
                    )
                    if not remember_me:
                        self.request.session.set_expiry(0)
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()
        return self.cleaned_data
