from django import forms
from .models import House, Section, Floor
from django.utils.translation import gettext_lazy as _
from django.forms import BaseModelFormSet, BaseFormSet
from django.contrib.auth import get_user_model

User = get_user_model()


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        exclude = ('user',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'})
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
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                  widget=forms.Select(attrs={'class': 'form-control user-select',
                                                             'onchange': "selectUser(this)"}))
    role = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                         'disabled': 'true'}))


