from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import House, Section, Floor
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


User = get_user_model()


# region House Forms


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        exclude = ('user',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'image1': forms.FileInput(attrs={'type': 'file'}),
            'image2': forms.FileInput(attrs={'type': 'file'}),
            'image3': forms.FileInput(attrs={'type': 'file'}),
            'image4': forms.FileInput(attrs={'type': 'file'}),
            'image5': forms.FileInput(attrs={'type': 'file'}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        exclude = ('house',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        exclude = ('house',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }


class UserFormSet(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True),
                                  empty_label='Выберите...',
                                  widget=forms.Select(attrs={'class': 'form-control user-select',
                                                             'onchange': "selectUser(this)"}))
    role = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'disabled': 'true'}))


# endregion House Forms


class OwnerForm(UserCreationForm):

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control pass-value'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control pass-value'}),
    )

    class Meta:
        model = User
        exclude = ('role', 'email')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control',
                                                    'type': 'date'}),
            'user_id': forms.TextInput(attrs={'class': 'form-control'}),
            'about_owner': forms.Textarea(attrs={'class': 'form-control', 'rows': '12'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'data-mask': "+38(000) 000-00-00"}),
            'viber': forms.TextInput(attrs={'class': 'form-control',
                                            'data-mask': "+38(000) 000-00-00"}),
            'telegram': forms.TextInput(attrs={'class': 'form-control',
                                               'data-mask': "+38(000) 000-00-00"}),
            'username': forms.EmailInput(attrs={'class': 'form-control'})

        }

    def clean_password2(self):
        print(self.cleaned_data)
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
