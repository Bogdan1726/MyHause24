from django import forms
from .models import House
from django.utils.translation import gettext_lazy as _


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        exclude = ('user', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'})
        }
        labels = {
            'title': _('Название')
        }
