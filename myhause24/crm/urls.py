from django.urls import path
from .views import HouseListView, index, HouseCreateView, HouseUpdateView, HouseDetailView, \
    OwnerListView, OwnerCreateView, OwnerUpdateView, OwnerDetailView, ApartmentListView, ApartmentCreateView, \
    ApartmentUpdateView, ApartmentDetailView, ApartmentDelete, invite_owner, OwnerDelete, HouseDelete, \
    AccountsListView, AccountsDetailView, AccountsCreateView, AccountsUpdateView, AccountsDelete
from .api_views import load_role, loading_floor_section, loading_personal_account, loading_section_for_house, \
    loading_apartment_for_section, loading_apartment_owner
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
    path('house/delete/<int:pk>/', HouseDelete.as_view(), name='delete_house'),
    # houses end

    # owners
    path('owner/invite/', invite_owner, name='invite_owner'),
    path('owner/', OwnerListView.as_view(), name='owners'),
    path('owner/create/', OwnerCreateView.as_view(), name='create_owner'),
    path('owner/<int:pk>/', OwnerDetailView.as_view(), name='detail_owner'),
    path('owner/update/<int:pk>/', OwnerUpdateView.as_view(), name='update_owner'),
    path('owner/delete/<int:pk>/', OwnerDelete.as_view(), name='delete_owner'),
    # owners end

    # apartments
    path('loading_floor_section/', loading_floor_section, name='loading_floor_section'),
    path('loading_personal_account/', loading_personal_account, name='loading_personal_account'),
    path('apartments/', ApartmentListView.as_view(), name='apartments'),
    path('apartment/create/', ApartmentCreateView.as_view(), name='create_apartment'),
    path('apartment/<int:pk>/', ApartmentDetailView.as_view(), name='detail_apartment'),
    path('apartment/update/<int:pk>/', ApartmentUpdateView.as_view(), name='update_apartment'),
    path('apartment/delete/<int:pk>/', ApartmentDelete.as_view(), name='delete_apartment'),
    # apartments end

    # accounts
    path('loading_section_for_house/', loading_section_for_house, name='loading_section_for_house'),
    path('loading_apartment_for_section/', loading_apartment_for_section, name='loading_apartment_for_section'),
    path('loading_apartment_owner/', loading_apartment_owner, name='loading_apartment_owner'),
    path('accounts/', AccountsListView.as_view(), name='accounts'),
    path('accounts/<int:pk>/', AccountsDetailView.as_view(), name='detail_accounts'),
    path('accounts/create/', AccountsCreateView.as_view(), name='create_accounts'),
    path('accounts/update/<int:pk>/', AccountsUpdateView.as_view(), name='update_accounts'),
    path('accounts/delete/<int:pk>/', AccountsDelete.as_view(), name='delete_accounts')

    # accounts end
]
