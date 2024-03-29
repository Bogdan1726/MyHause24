from django.views.generic import DetailView
from .models import HomePage, Contact, AboutUs, Document, SiteService


# Create your views here.

# region HomePage


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


class AboutUsListView(DetailView):
    model = AboutUs
    template_name = 'main/pages/about_page.html'
    context_object_name = 'about'

    def get_object(self, queryset=None):
        AboutUs.objects.get_or_create(id=1)
        obj = AboutUs.objects.filter(id=1).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = Document.objects.filter(page=self.object).select_related('page')
        return context


class ServicesPageListView(DetailView):
    model = SiteService
    template_name = 'main/pages/services_page.html'
    context_object_name = 'service'

    def get_object(self, queryset=None):
        SiteService.objects.get_or_create(id=1)
        obj = SiteService.objects.filter(id=1).first()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_services'] = SiteService.objects.all().select_related('seo_block')
        return context


# endregion HomePage

