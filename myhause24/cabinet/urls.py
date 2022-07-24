from django.urls import path
from .views import (
    StatisticsOfCabinetListView, ProfileDetailView, ProfileUpdateView, MasterCallListView,
    MasterCallDelete, MasterCallCreateView, MessagesListView, MessageDetailView,
    MessageDelete, ServicesOfTariffListView, ReceiptOfOwnerListView, ReceiptOfOwnerDetailView,
    pay_by_receipt, export_pdf, receipt_print
)

urlpatterns = [
    path('', StatisticsOfCabinetListView.as_view(), name='cabinet'),

    # region Receipts
    path('receipts/', ReceiptOfOwnerListView.as_view(), name='list-receipts'),
    path('receipt/<int:pk>/', ReceiptOfOwnerDetailView.as_view(), name='detail-receipt'),
    path('receipt/pay/<int:pk>/', pay_by_receipt, name='pay_by_receipt'),
    path('receipt/download/pdf/<int:pk>/', export_pdf, name='export_pdf'),
    path('receipt/print/<int:pk>', receipt_print, name='receipt_print'),
    # endregion Receipts

    # region Tariff
    path('tariff/', ServicesOfTariffListView.as_view(), name='list-tariff'),
    # endregion Tariff

    # region messages
    path('messages/', MessagesListView.as_view(), name='list-messages'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='detail-message'),
    path('message/delete/<int:pk>/', MessageDelete.as_view(), name='delete-message'),
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
