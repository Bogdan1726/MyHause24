from django.urls import path
from .views import HomePageListView, ContactPageListView

urlpatterns = [
    path('', HomePageListView.as_view(), name='main'),
    path('contact/', ContactPageListView.as_view(), name='contact'),
]
