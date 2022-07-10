import os
import uuid
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.shortcuts import get_object_or_404
from .models import House, Section, Floor, Apartment, PersonalAccount, UnitOfMeasure, Services, \
    Tariff, PriceTariffServices, Requisites, PaymentItems, MeterData, CallRequest, CashBox, Receipt, \
    CalculateReceiptService, ReceiptTemplate, Message
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from user.models import Role
from main.models import HomePage, SeoBlock, ContentBlock, Contact, AboutUs, Gallery, SiteService, Document

from .task import send_new_password_owner

User = get_user_model()


# region Receipts Forms

class ReceiptForm(forms.ModelForm):
    error_messages = {
        'len_number': _('Длина номера должна быть не менее 8 символов..'),
    }

    house = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'}))

    section = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'}))

    personal_accounts = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    class Meta:
        model = Receipt
        fields = "__all__"

        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',
                                             'data-mask': '00000000'}),
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'apartment': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput({'class': 'form-check-input'}),
            'status_pay': forms.Select(attrs={'class': 'form-control'}),
            'tariff': forms.Select(attrs={'class': 'form-control'}),
            'date_start': forms.DateInput(attrs={'class': 'form-control'}),
            'date_end': forms.DateInput(attrs={'class': 'form-control'}),

        }

    def __init__(self, *args, **kwargs):
        super(ReceiptForm, self).__init__(*args, **kwargs)
        self.fields['apartment'].empty_label = 'Выберите...'
        self.fields['tariff'].empty_label = 'Выберите...'
        self.fields['house'].choices = [('', 'Выберите...')] + [(obj.id, obj.title) for obj in House.objects.all()]
        self.fields['section'].choices = [('', 'Выберите...')] + [(obj.id, obj.title) for obj in Section.objects.all()]
        self.fields['personal_accounts'].choices = \
            [('', '')] + [(obj.id, obj.number) for obj in PersonalAccount.objects.filter(
                status='active'
            )]
        self.fields['number'].error_messages = {'unique': 'Квитанция с таким номером уже существует.'}

    def clean_number(self):
        number = self.cleaned_data.get("number")
        if len(number) < 8:
            raise ValidationError(
                self.error_messages['len_number'],
            )
        return number


class CalculateReceiptServiceForm(forms.ModelForm):
    unit = forms.CharField(required=False,
                           initial='Выберите услугу',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'readonly': 'true'}))

    class Meta:
        model = CalculateReceiptService
        exclude = ('receipt',)

        widgets = {
            'services': forms.Select(attrs={'class': 'form-control',
                                            'onchange': "selectServices(this)"}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control',
                                                 'onchange': "calcСost(this)"}),
            'price': forms.NumberInput(attrs={'class': 'form-control',
                                              'onchange': "calcСost(this)"}),
            'cost': forms.NumberInput(attrs={'class': 'form-control total_cost'})
        }

    def __init__(self, *args, **kwargs):
        super(CalculateReceiptServiceForm, self).__init__(*args, **kwargs)
        self.fields['services'].empty_label = 'Выберите...'
        self.fields['services'].error_messages = {'required': _('Выберите услугу.')}
        self.fields['price'].error_messages = {'required': _('Цена обязательое поле.')}
        self.fields['quantity'].error_messages = {'required': _('Расход обязательное поле.')}
        self.fields['cost'].error_messages = {'required': _('Стоимость обязательное поле.')}


class SettingsTemplatesForm(forms.ModelForm):
    class Meta:
        model = ReceiptTemplate
        exclude = ('is_default',)

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


# endregion Receipts Form


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

# region Message Form

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ('datetime', 'is_all',)

        widgets = {
            'topics': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Тема сообщения:'}),
            'text': forms.Textarea(attrs={'class': 'form-control',
                                          'placeholder': 'Текст сообщения:'}),
            'is_dept': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'house': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'apartment': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['house'].empty_label = 'Всем...'
        self.fields['section'].empty_label = 'Всем...'
        self.fields['floor'].empty_label = 'Всем...'
        self.fields['apartment'].empty_label = 'Всем...'


# endregion Message Form


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
            send_new_password_owner.delay(
                self.cleaned_data['username'],
                self.cleaned_data['new_password1']
            )
        if commit:
            user.save()
        return user


class InviteOwnerForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': '+380991234567',
                                      'data-mask': "+38(000) 000-00-00"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'info@example.com'})
    )


# endregion Owner Form


# region Apartment Form

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = "__all__"
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'house': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'floor': forms.Select(attrs={'class': 'form-control'}),
            'tariff': forms.Select(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(ApartmentForm, self).__init__(*args, **kwargs)
        self.fields['section'].empty_label = 'Выберите...'
        self.fields['floor'].empty_label = 'Выберите...'
        self.fields['house'].empty_label = 'Выберите...'
        self.fields['tariff'].empty_label = 'Выберите...'
        self.fields['owner'].empty_label = 'Выберите...'
        self.fields['owner'].queryset = User.objects.filter(is_staff=False)


class PersonalAccountForm(forms.ModelForm):
    list_personal_accounts = forms.ModelChoiceField(queryset=PersonalAccount.objects.filter(
        status='active',
        apartment=None
    ),
        empty_label='Выберите...',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    number_account = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                   'data-mask': "00000-00000"}))

    class Meta:
        model = PersonalAccount
        exclude = ('status', 'apartment', 'number')

        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',
                                             'data-mask': "00000-00000"})
        }


# endregion Apartment Form


# region Accounts Form

class AccountsForm(forms.ModelForm):
    house = forms.ModelChoiceField(queryset=House.objects.all(),
                                   empty_label='Выберите...',
                                   required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    section = forms.ModelChoiceField(queryset=Section.objects.all(),
                                     empty_label='Выберите...',
                                     required=False,
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = PersonalAccount
        fields = '__all__'

        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',
                                             'data-mask': '00000-00000'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'apartment': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(AccountsForm, self).__init__(*args, **kwargs)
        self.fields['apartment'].empty_label = 'Выберите...'
        self.fields['number'].error_messages = {'unique': _('Лицевой счет с таким номером уже существует.')}


# endregion Accounts Form


# region Services Form

class UnitOfMeasureForm(forms.ModelForm):
    class Meta:
        model = UnitOfMeasure
        fields = ('title',)

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(UnitOfMeasureForm, self).__init__(*args, **kwargs)
        self.fields['title'].error_messages = {'unique': 'Единица измерения с таким заголовком уже существует..'}


class ServicesForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = "__all__"

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'u_measurement': forms.Select(attrs={'class': 'form-control'}),
            'is_show_meter_data': forms.CheckboxInput({'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super(ServicesForm, self).__init__(*args, **kwargs)
        self.fields['u_measurement'].empty_label = 'Выберите...'
        self.fields['title'].error_messages = {'required': 'Поле Услуга не может быть пустым.'}


# endregion Services Form


# region Tariff Form

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        exclude = ('date_edit',)

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': '6'})
        }


class PriceTariffServicesForm(forms.ModelForm):
    currency = forms.CharField(required=False,
                               initial='грн',
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'readonly': 'true'}))

    unit = forms.CharField(required=False,
                           initial='Выберите...',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'readonly': 'true'}))

    class Meta:
        model = PriceTariffServices
        exclude = ('tariff',)

        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'services': forms.Select(attrs={'class': 'form-control',
                                            'onchange': "selectServices(this)"})
        }

    def __init__(self, *args, **kwargs):
        super(PriceTariffServicesForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.fields['unit'].initial = kwargs.get('instance').services.u_measurement
        self.fields['services'].empty_label = 'Выберите...'
        self.fields['price'].error_messages = {'required': 'Поле цена в форме услуги является обязательным полем'}


# endregion Tariff Form


# region Roles
class RolesForm(forms.ModelForm):
    class Meta:
        model = Role
        exclude = ('name',)


# endregion Roles

# region Requisites


class RequisitesForm(forms.ModelForm):
    class Meta:
        model = Requisites
        fields = '__all__'

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': '6'})
        }


# endregion Requisites

# region User Forms
class UserAdminForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    password1 = forms.CharField(
        label=_("New password"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control pass-value',
                                          'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_("New password confirmation"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control pass-value',
                                          'autocomplete': 'new-password'}),
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone', 'role',
                  'status', 'password1', 'password2')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'data-mask': "+38(000) 000-00-00"}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.EmailInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['role'].empty_label = 'Выберите...'

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
        while True:
            unique_id = uuid.uuid4().hex[:6]
            if not User.objects.filter(user_id=unique_id).exists():
                user.user_id = unique_id
                break
        user.is_staff = True
        if self.cleaned_data.get('password1') != '':
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(UserChangeForm):
    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
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
        fields = ('username', 'first_name', 'last_name', 'phone', 'role',
                  'status', 'new_password1', 'new_password2')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control',
                                            'data-mask': "+38(000) 000-00-00"}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.EmailInput(attrs={'class': 'form-control'})

        }

    def __init__(self, *args, **kwargs):
        super(UserAdminChangeForm, self).__init__(*args, **kwargs)
        self.fields['role'].empty_label = 'Выберите...'
        self.fields['status'].required = False

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
        if user.is_superuser:
            user.role = get_object_or_404(Role, id=1)
        user.email = self.cleaned_data['username']
        if self.cleaned_data.get('new_password1') != '':
            user.set_password(self.cleaned_data["new_password1"])
            send_new_password_owner.delay(
                self.cleaned_data['username'],
                self.cleaned_data['new_password1']
            )
        if commit:
            user.save()
        return user


# endregion User Forms


# region Payment Items Forms

class PaymentItemsForm(forms.ModelForm):
    class Meta:
        model = PaymentItems
        fields = '__all__'

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'})
        }


# endregion Payment Items Forms

# region MasterCall Forms

class MasterCallForm(forms.ModelForm):
    error_messages = {
        'apartment_required': _('Необходимо выбрать квартиру.'),
    }

    owner = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    apartment = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    class Meta:
        model = CallRequest
        exclude = ('apartment',)

        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'time': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'type_master': forms.Select(attrs={'class': 'form-control'}),
            'master': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(MasterCallForm, self).__init__(*args, **kwargs)
        self.fields['type_master'].empty_label = 'Выберите...'
        self.fields['type_master'].queryset = Role.objects.exclude(id__in=[1, 2, 3])
        self.fields['master'].empty_label = 'Выберите...'
        self.fields['master'].queryset = User.objects.filter(is_staff=True)
        self.fields['apartment'].choices = \
            [('', '')] + [(obj.id, obj.select2) for obj in Apartment.objects.all().select_related(
                'house', 'owner', 'section', 'floor'
            )]
        self.fields['owner'].choices = \
            [('', '')] + [(obj.id, obj.__str__) for obj in User.objects.filter(is_staff=False)]

    def clean_apartment(self):
        apartment = self.cleaned_data.get("apartment")
        if not apartment:
            raise ValidationError(
                self.error_messages['apartment_required'],
            )
        return apartment

    def save(self, commit=True):
        master_call = super().save(commit=False)
        apartment_id = self.cleaned_data['apartment']
        if apartment_id:
            obj = get_object_or_404(Apartment, id=apartment_id)
            master_call.apartment = obj
        if commit:
            master_call.save()
        return master_call


# endregion MasterCall Forms


# region MeterData Forms
class MeterDataForm(forms.ModelForm):
    house = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )
    section = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )

    class Meta:
        model = MeterData
        fields = ('number', 'date', 'apartment', 'counter', 'status', 'indications')

        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',
                                             'data-mask': '00000000'}),
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'apartment': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'counter': forms.Select(attrs={'class': 'form-control'}),
            'indications': forms.NumberInput(attrs={'class': 'form-control'})

        }

    def __init__(self, *args, **kwargs):
        super(MeterDataForm, self).__init__(*args, **kwargs)
        self.fields['house'].choices = [('', 'Выберите...')] + [(obj.id, obj.title) for obj in House.objects.all()]
        self.fields['section'].choices = [('', 'Выберите...')] + [(obj.id, obj.title) for obj in Section.objects.all()]
        self.fields['apartment'].empty_label = 'Выберите...'
        self.fields['counter'].empty_label = 'Выберите...'
        self.fields['counter'].queryset = Services.objects.filter(is_show_meter_data=True)
        self.fields['number'].error_messages = {'unique': 'Данные счетчика с таким номером уже существует.'}


# endregion MeterData Forms


# region CashBox Forms

class CashBoxForm(forms.ModelForm):
    error_messages = {
        'len_number': _('Длина номера должна быть не менее 10 символов..'),
    }
    owner = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    personal_account = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control select2 select2-hidden-accessible',
            'style': 'width: 100%;'}))

    manager = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )

    class Meta:
        model = CashBox
        exclude = ('receipt', 'manager', 'owner', 'personal_account', 'type')

        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control',
                                             'data-mask': '0000000000'}),
            'date': forms.DateInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control',
                                             'rows': 7}),
            'payment_items': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput({'class': 'form-check-input'}),
            'sum': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CashBoxForm, self).__init__(*args, **kwargs)
        self.fields['payment_items'].empty_label = 'Выберите...'
        self.fields['number'].error_messages = {'unique': 'Ведомость с таким номером уже существует.'}
        self.fields['payment_items'].queryset = PaymentItems.objects.filter(type=kwargs['initial'].get('type_pay'))
        self.fields['owner'].choices = \
            [('', '')] + [(obj.id, obj.__str__) for obj in User.objects.filter(is_staff=False)]
        self.fields['personal_account'].choices = \
            [('', '')] + [(obj.id, obj.number) for obj in PersonalAccount.objects.all()]
        self.fields['manager'].choices = [(obj.id, obj.role_str) for obj in User.objects.filter(
            is_staff=True, role__in=[1, 2, 3]).select_related('role')]

    def clean_number(self):
        number = self.cleaned_data.get("number")
        if len(number) < 10:
            raise ValidationError(
                self.error_messages['len_number'],
            )
        return number

    def save(self, commit=True):
        cash = super().save(commit=False)
        print(cash)
        print(self.cleaned_data)
        manager = self.cleaned_data['manager']
        owner = self.cleaned_data['owner']
        personal_account = self.cleaned_data['personal_account']
        if manager:
            obj = get_object_or_404(User, id=manager)
            cash.manager = obj
        if owner:
            obj = get_object_or_404(User, id=owner)
            cash.owner = obj
        if personal_account:
            obj = get_object_or_404(PersonalAccount, id=personal_account)
            cash.personal_account = obj
        if commit:
            cash.save()
        return cash


# endregion CashBox Forms


# region SiteForms

class ContentBlockForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображений не соответствует параметрам',
    }

    class Meta:
        model = ContentBlock
        fields = "__all__"

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control content_des'}),
            'image': forms.FileInput(attrs={'type': 'file'})
        }

    def clean_image(self):
        image = self.cleaned_data['image']
        width, height = get_image_dimensions(image)
        if width != 1000 or height != 600:
            raise forms.ValidationError(
                self.error_messages['error_image']
            )
        return image


class SeoBlockForm(forms.ModelForm):
    class Meta:
        model = SeoBlock
        fields = "__all__"

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'rows': 6}),
            'keywords': forms.Textarea(attrs={'class': 'form-control',
                                              'rows': 6})
        }


class HomePageForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображений не соответствует параметрам',
    }

    class Meta:
        model = HomePage
        exclude = ('content_block', 'seo_block')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'is_show_link': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'slide1': forms.FileInput(attrs={'type': 'file'}),
            'slide2': forms.FileInput(attrs={'type': 'file'}),
            'slide3': forms.FileInput(attrs={'type': 'file'}),

        }

    def clean(self):
        images = ['slide1', 'slide2', 'slide3']
        for image in images:
            if self.cleaned_data[image]:
                width, height = get_image_dimensions(self.cleaned_data[image])
                if width != 1920 or height != 800:
                    raise forms.ValidationError(
                        self.error_messages['error_image']
                    )
        return self.cleaned_data


class ContactPageForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ('seo_block',)

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'initials': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'maps': forms.Textarea(attrs={'class': 'form-control',
                                          'rows': 6})

        }


class AboutPageForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображений не соответствует параметрам',
    }

    gallery_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'type': 'file'})
    )

    gallery2_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'type': 'file'})
    )

    class Meta:
        model = AboutUs
        exclude = ('seo_block', 'gallery', 'gallery2')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control description'}),
            'title2': forms.TextInput(attrs={'class': 'form-control'}),
            'description2': forms.Textarea(attrs={'class': 'form-control description'}),
            'image': forms.FileInput(attrs={'type': 'file'}),
        }

    def clean_image(self):
        image = self.cleaned_data['image']
        width, height = get_image_dimensions(image)
        if width != 250 or height != 310:
            raise forms.ValidationError(
                self.error_messages['error_image']
            )
        return image


class GalleryForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображений не соответствует параметрам',
    }

    class Meta:
        model = Gallery
        fields = '__all__'

        widgets = {
            'image': forms.FileInput(attrs={'type': 'file'})
        }

    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            width, height = get_image_dimensions(image)
            if width != 1200 or height != 1200:
                raise forms.ValidationError(
                    self.error_messages['error_image']
                )
        return image


class DocumentForm(forms.ModelForm):
    ALLOWED_TYPES = ['pdf', 'jpg']

    error_messages = {
        'size': 'Превышен максимально допустимый размер файла',
        'type': 'Тип загружаемого файла не разрешен'
    }

    class Meta:
        model = Document
        exclude = ('page',)

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'type': 'file'})
        }

    def clean_file(self):
        file = self.cleaned_data['file']
        extension = os.path.splitext(file.name)[1][1:].lower()
        if file.size > 20971520:
            raise ValidationError(
                self.error_messages['size']
            )
        if extension not in self.ALLOWED_TYPES:
            raise ValidationError(
                self.error_messages['type']
            )
        return file

# endregion SiteForms
