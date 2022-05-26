from django.urls import path, reverse_lazy
from django.views.generic import DeleteView
from .models import House
from .views import HouseListView, index, HouseCreateView, HouseUpdateView, HouseDetailView, \
    OwnerListView, OwnerCreateView, OwnerUpdateView, OwnerDetailView
from .services.load_role_of_formset_house import load_role
from django.contrib.auth import get_user_model

User = get_user_model()

urlpatterns = [
    path('', index, name='admin'),

    # house
    path('load_role/', load_role, name='load_role'),
    path('house/', HouseListView.as_view(), name='houses'),
    path('house/create/', HouseCreateView.as_view(), name='create_house'),
    path('house/<int:pk>/', HouseDetailView.as_view(), name='detail_house'),
    path('house/update/<int:pk>/', HouseUpdateView.as_view(), name='update_house'),
    path('house/delete/<int:pk>/', DeleteView.as_view(
        model=House, success_url=reverse_lazy('houses')), name='delete_house'),
    # houses end

    # owners
    path('owner/', OwnerListView.as_view(), name='owners'),
    path('owner/create/', OwnerCreateView.as_view(), name='create_owner'),
    path('owner/<int:pk>/', OwnerDetailView.as_view(), name='detail_owner'),
    path('owner/update/<int:pk>/', OwnerUpdateView.as_view(), name='update_owner'),
    path('owner/delete/<int:pk>/', DeleteView.as_view(
        model=User, success_url=reverse_lazy('owners')), name='delete_owner'),

    # owners end
]
