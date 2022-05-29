from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import House, Section, Floor, Apartment, Tariff
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# region House Forms


class HouseForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображений не соответствует параметрам',
    }

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

    def clean(self):
        images = ['image1', 'image2', 'image3', 'image4', 'image5']
        for image in images:
            if self.cleaned_data[image]:
                width, height = get_image_dimensions(self.cleaned_data[image])
                if image == 'image1':
                    if width != 522 or height != 350:
                        raise forms.ValidationError(
                            self.error_messages['error_image']
                        )
                else:
                    if width != 248 or height != 160:
                        raise forms.ValidationError(
                            self.error_messages['error_image']
                        )
        return self.cleaned_data


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
                                                                         'readonly': 'true'}))


# endregion House Forms

# region Owner Form
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
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'password1', 'password2',
                  'date_of_birth', 'user_id', 'about_owner', 'phone', 'telegram', 'viber',
                  'status', 'profile_picture')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
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
        user.email = self.cleaned_data['username']
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class OwnerUpdateForm(UserChangeForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
        'duplicate_user_id': _('Владелец с данным ID уже существует!')
    }

    new_password1 = forms.CharField(
        label=_("New password"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control pass-value',
                                          'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control pass-value',
                                          'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'patronymic', 'new_password1', 'new_password2',
                  'date_of_birth', 'user_id', 'about_owner', 'phone', 'telegram', 'viber',
                  'status', 'profile_picture')

        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control'}),
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

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return new_password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username']
        if self.cleaned_data.get('new_password1') != '':
            user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


# endregion Owner Form


# region Apartment Form


class ApartmentForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.none(),
                                     empty_label='Выберите...',
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    floor = forms.ModelChoiceField(queryset=Floor.objects.none(),
                                   empty_label='Выберите...',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    house = forms.ModelChoiceField(queryset=House.objects.all(),
                                   empty_label='Выберите...',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    owner = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False),
                                   empty_label='Выберите...',
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    tariff = forms.ModelChoiceField(queryset=Tariff.objects.all(),
                                    required=False,
                                    empty_label='Выберите...',
                                    widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Apartment
        fields = "__all__"
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
            'personal_account': forms.TextInput(attrs={'class': 'form-control'})
        }

# endregion Apartment Form
