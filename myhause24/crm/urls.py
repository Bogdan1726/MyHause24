from django.urls import path
from .views import HouseListView, index, HouseCreateView, HouseUpdateView

urlpatterns = [
    path('', index, name='admin'),

    # house
    path('house/', HouseListView.as_view(), name='houses'),
    path('house/create/', HouseCreateView.as_view(), name='create_house'),
    path('house/update/<int:pk>/', HouseUpdateView.as_view(), name='update_house')

    # houses end
]
