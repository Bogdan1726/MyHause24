from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import User
from django.utils.translation import gettext_lazy as _
from snowpenguin.django.recaptcha3.fields import ReCaptchaField


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                       'autocomplete': 'off',
                                       'class': 'form-control'}))

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
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


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control pass-value',
                                          'placeholder': _("Password")}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control pass-value',
                                          'placeholder': _("Password confirmation")}),
    )

    is_agree = forms.BooleanField(required=True, initial=True,
                                  widget=forms.CheckboxInput(
                                      attrs={'class': 'form-check-input'}))

    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('username', 'last_name', 'password1', 'password2')
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'ФИО',
                                                'required': True}),
            'username': forms.EmailInput(attrs={'class': 'form-control',
                                                'placeholder': 'E-mail'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields['username'].widget.attrs['autofocus'] = False

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    @staticmethod
    def generate_number():
        counter = 1
        while True:
            try:
                obj_id = User.objects.order_by('-id').first().id
            except AttributeError:
                obj_id = 0
            number = f'{obj_id + counter:06}'
            if not User.objects.filter(user_id=number).exists():
                return number
            counter += 1

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['last_name'].split(' ')
        if len(full_name) == 3:
            user.last_name = full_name[0]
            user.first_name = full_name[1]
            user.patronymic = full_name[2]
        elif len(full_name) == 2:
            user.last_name = full_name[0]
            user.first_name = full_name[1]
        user.email = self.cleaned_data['username']
        user.user_id = self.generate_number()
        user.is_active = False
        user.status = 'disabled'
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    # def clean_password2(self):
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
    #     return password2
    #
    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data['password1'])
    #     user.is_active = False
    #     user.status = 'disable'
    #     if commit:
    #         user.save()
    #     user_registered.send(RegisterUserForm, instance=user)
    #     return user
