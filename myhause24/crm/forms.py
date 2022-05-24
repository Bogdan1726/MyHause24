from django import forms
from django.core.files.images import get_image_dimensions

from .models import House, Section, Floor
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class HouseForm(forms.ModelForm):
    error_messages = {
        'error_image': 'Размер изображения должен быть 248x160',
        'error_image2': 'Размер изображения должен быть 522x350'
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

    # def clean(self):
    #     images = ['image1', 'image2', 'image3', 'image4', 'image5']
    #     for image in images:
    #         width, height = get_image_dimensions(self.cleaned_data[image])
    #         if width != 248 or height != 160:
    #             raise forms.ValidationError(
    #                 self.error_messages['error_image']
    #             )
    #     return self.cleaned_data


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
