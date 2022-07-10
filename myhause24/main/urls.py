from django.urls import path
from .views import HomePageListView, ContactPageListView, index

urlpatterns = [
    path('', HomePageListView.as_view(), name='main'),
    path('contact/', ContactPageListView.as_view(), name='contact'),
    path('about/', index, name='about')
]
