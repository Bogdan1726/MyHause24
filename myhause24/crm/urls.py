from django.urls import path, reverse_lazy
from django.views.generic import DeleteView
from .models import House
from .views import HouseListView, index, HouseCreateView, HouseUpdateView, HouseDetailView, OwnerListView, \
    OwnerCreateView
from .services.load_role_of_formset_house import load_role

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
    path('owners/', OwnerListView.as_view(), name='owners'),
    path('owners/create/', OwnerCreateView.as_view(), name='create_owner')

    # owners end
]
