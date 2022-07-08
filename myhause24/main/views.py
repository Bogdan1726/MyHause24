from django.shortcuts import render
from django.views.generic import ListView, DetailView

# Create your views here.

# region HomePage
from .models import HomePage, Contact


class HomePageListView(DetailView):

    model = HomePage
    template_name = 'main/pages/home_page.html'
    context_object_name = 'home_page'

    def get_object(self, queryset=None):
        HomePage.objects.get_or_create(id=1)
        obj = HomePage.objects.filter(id=1).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact'] = Contact.objects.all().first()
        return context


class ContactPageListView(DetailView):

    model = Contact
    template_name = 'main/pages/contact_page.html'
    context_object_name = 'contact'

    def get_object(self, queryset=None):
        Contact.objects.get_or_create(id=1)
        obj = Contact.objects.filter(id=1).first()
        return obj

# endregion HomePage

