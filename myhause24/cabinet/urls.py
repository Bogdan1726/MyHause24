from django.urls import path
from .views import (
    SummaryListView, ProfileDetailView, ProfileUpdateView, MasterCallListView,
    MasterCallDelete, MasterCallCreateView, MessagesListView, MessageDetailView,
    MessageDelete
)

urlpatterns = [
    path('', SummaryListView.as_view(), name='cabinet'),

    # region messages
    path('messages/', MessagesListView.as_view(), name='list-messages'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='detail-message'),
    path('messages/delete/<int:pk>/', MessageDelete.as_view(), name='delete-message'),

    # endregion messages

    # region master's call
    path('master-call/', MasterCallListView.as_view(), name='master-call'),
    path('master-call/create/', MasterCallCreateView.as_view(), name='create_master-call'),
    path('master-call/delete/<int:pk>/', MasterCallDelete.as_view(), name='delete_master-call'),
    # endregion master's call

    # region profile
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='update_profile'),
    # endregion profile

]
