from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.db.models import Q

from .models import User
from django.utils.translation import gettext_lazy as _


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

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
            if '/admin/' in self.request.POST['redirect']:
                try:
                    User.objects.get(email=username, is_staff=True)
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()
            if '/cabinet/' in self.request.POST['redirect']:
                try:
                    User.objects.get(
                        Q(email=username) | Q(user_id=username), is_staff=False
                    )
                except User.DoesNotExist:
                    raise self.get_invalid_login_error()

        return self.cleaned_data
