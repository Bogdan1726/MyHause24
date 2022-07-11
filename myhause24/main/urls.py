from django.urls import path
from .views import HomePageListView, ContactPageListView, AboutUsListView, ServicesPageListView

urlpatterns = [
    path('', HomePageListView.as_view(), name='main'),
    path('contact/', ContactPageListView.as_view(), name='contact'),
    path('about/', AboutUsListView.as_view(), name='about'),
    path('services/', ServicesPageListView.as_view(), name='site_services')
]
