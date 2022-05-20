from django import forms
from .models import House, Section, Floor
from django.utils.translation import gettext_lazy as _
from django.forms import BaseModelFormSet


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


# class FormsetForSection(BaseModelFormSet):
#
#     def save(self, commit=True, **kwargs):
#         print('save form')
#         print(kwargs.get('obj'))
#         """
#         Save model instances for every form, adding and changing instances
#         as necessary, and return the list of instances.
#         """
#         if not commit:
#             self.saved_forms = []
#             print(self.saved_forms)
#
#             def save_m2m():
#                 for form in self.saved_forms:
#                     form.save_m2m()
#
#             self.save_m2m = save_m2m
#         return self.save_existing_objects(commit) + self.save_new_objects(commit)
