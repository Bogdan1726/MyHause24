from django.urls import path
from django.contrib.auth import get_user_model
from .views import (
    HouseListView, HouseCreateView, HouseUpdateView, HouseDetailView,
    OwnerListView, OwnerCreateView, OwnerUpdateView, OwnerDetailView, ApartmentListView,
    ApartmentCreateView, ApartmentUpdateView, ApartmentDetailView, ApartmentDelete,
    invite_owner, OwnerDelete, HouseDelete, AccountsListView, AccountsDetailView,
    AccountsCreateView, AccountsUpdateView, AccountsDelete, ServicesListView,
    TariffListView, TariffDetailView, TariffCreateView, TariffUpdateView, TariffDelete,
    RolesUpdateView, RequisitesView, UsersListView, UserDetailView, UserCreateView,
    UserUpdateView, UserDelete, PaymentItemsListView, PaymentItemsCreateView, PaymentItemsDetailView,
    PaymentItemsUpdateView, PaymentItemsDelete, MeterDataListView, MeterDataCreateView, MeterDataApartmentListView,
    MeterDataUpdateView, MeterDataDelete, MeterDataDetailView, MasterCallListView, MasterCallDetailView,
    MasterCallCreateView, MasterCallUpdateView, MasterCallDelete, CashBoxListView, CashBoxDetailView, CashBoxCreateView,
    CashBoxDelete, CashBoxUpdateView, ReceiptListView, ReceiptCreateView, ReceiptUpdateView, ReceiptDelete,
    ReceiptDetailView, ReceiptTemplateListView, receipt_template, SettingsTemplate, ReceiptTemplateDelete,
    receipt_templates_edit, receipt_templates_upload, MessageCreateAndSend, MessageDetailView,
    MessageDelete, MessageListView, StatisticsView, SiteHomePage, SiteContactPage, SiteAboutPage, DeleteDocument,
    DeleteGalleryImage, SiteServicesPage, DeleteSiteServices, update_robots_and_sitemap
)
from .api_views import (
    load_role, loading_floor_section, loading_personal_account, loading_section_for_house,
    loading_apartment_for_section, loading_apartment_owner, check_units, loading_unit_for_services,
    send_invite, new_users, loading_apartment_of_owner, loading_master_of_type_master,
    loading_personal_account_of_owner, loading_services_for_tariff, meter_data_for_receipt, delete_is_checked_receipts,
    loading_apartment_for_message, delete_is_checked_messages, check_services,
)

User = get_user_model()

urlpatterns = [
    # region statistics
    path('', StatisticsView.as_view(), name='admin'),
    # endregion

    # region cash_box urls
    path('cashbox/', CashBoxListView.as_view(), name='cash_box'),
    path('cashbox/<int:pk>/', CashBoxDetailView.as_view(), name='detail_cash_box'),
    path('cashbox/create/', CashBoxCreateView.as_view(), name='create_cash_box'),
    path('cashbox/delete/<int:pk>/', CashBoxDelete.as_view(), name='delete_cash_box'),
    path('cashbox/update/<int:pk>/', CashBoxUpdateView.as_view(), name='update_cash_box'),
    # endregion cash_box urls

    # region receipts urls
    path('receipts/', ReceiptListView.as_view(), name='receipts'),
    path('receipt/create/', ReceiptCreateView.as_view(), name='create_receipt'),
    path('receipt/update/<int:pk>/', ReceiptUpdateView.as_view(), name='update_receipt'),
    path('receipt/delete/<int:pk>/', ReceiptDelete.as_view(), name='delete_receipt'),
    path('receipt/<int:pk>/', ReceiptDetailView.as_view(), name='detail_receipt'),
    path('receipt/templates/<int:pk>/', ReceiptTemplateListView.as_view(), name='template_receipt'),
    path('receipt/templates/settings/<int:pk>/', SettingsTemplate.as_view(), name='settings_templates'),
    path('receipt/templates/delete/<int:pk>/<slug:slug>/', ReceiptTemplateDelete.as_view(), name='delete_template'),
    path('receipt/templates/edit/<int:pk>/<slug:slug>/', receipt_templates_edit, name='edit_template'),
    path('receipt/templates/upload/<int:pk>/', receipt_templates_upload, name='upload_template'),
    path('receipt/<int:pk>/templates/send/', receipt_template, name='receipt_template'),
    # endregion receipts urls

    # region house
    path('house/', HouseListView.as_view(), name='houses'),
    path('house/create/', HouseCreateView.as_view(), name='create_house'),
    path('house/<int:pk>/', HouseDetailView.as_view(), name='detail_house'),
    path('house/update/<int:pk>/', HouseUpdateView.as_view(), name='update_house'),
    path('house/delete/<int:pk>/', HouseDelete.as_view(), name='delete_house'),
    # endregion houses

    # region messages
    path('message/', MessageListView.as_view(), name='list_message'),
    path('message/send/', MessageCreateAndSend.as_view(), name='send_message'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='detail_message'),
    path('message/delete/<int:pk>/', MessageDelete.as_view(), name='delete_message'),
    # endregion messages

    # region owners
    path('owner/invite/', invite_owner, name='invite_owner'),
    path('owner/', OwnerListView.as_view(), name='owners'),
    path('owner/create/', OwnerCreateView.as_view(), name='create_owner'),
    path('owner/<int:pk>/', OwnerDetailView.as_view(), name='detail_owner'),
    path('owner/update/<int:pk>/', OwnerUpdateView.as_view(), name='update_owner'),
    path('owner/delete/<int:pk>/', OwnerDelete.as_view(), name='delete_owner'),
    # endregion owners

    # region apartments
    path('apartments/', ApartmentListView.as_view(), name='apartments'),
    path('apartment/create/', ApartmentCreateView.as_view(), name='create_apartment'),
    path('apartment/<int:pk>/', ApartmentDetailView.as_view(), name='detail_apartment'),
    path('apartment/update/<int:pk>/', ApartmentUpdateView.as_view(), name='update_apartment'),
    path('apartment/delete/<int:pk>/', ApartmentDelete.as_view(), name='delete_apartment'),
    # endregion apartments

    # region accounts
    path('accounts/', AccountsListView.as_view(), name='accounts'),
    path('accounts/<int:pk>/', AccountsDetailView.as_view(), name='detail_accounts'),
    path('accounts/create/', AccountsCreateView.as_view(), name='create_accounts'),
    path('accounts/update/<int:pk>/', AccountsUpdateView.as_view(), name='update_accounts'),
    path('accounts/delete/<int:pk>/', AccountsDelete.as_view(), name='delete_accounts'),
    # endregion accounts

    # region master's call
    path('master-calls/', MasterCallListView.as_view(), name='master_calls'),
    path('master-call/<int:pk>/', MasterCallDetailView.as_view(), name='detail_master_call'),
    path('master-call/create/', MasterCallCreateView.as_view(), name='create_master_call'),
    path('master-call/update/<int:pk>/', MasterCallUpdateView.as_view(), name='update_master_call'),
    path('master-call/delete/<int:pk>/', MasterCallDelete.as_view(), name='delete_master_call'),
    # endregion master's call

    # region meter_data
    path('meter-data/', MeterDataListView.as_view(), name='meter_data'),
    path('meter-data/apartment/<int:pk>/', MeterDataApartmentListView.as_view(),
         name='meter_data_for_apartment'),
    path('meter-data/create/', MeterDataCreateView.as_view(), name='create_meter_data'),
    path('meter-data/<int:pk>/', MeterDataDetailView.as_view(), name='detail_meter_data'),
    path('meter-data/update/<int:pk>/', MeterDataUpdateView.as_view(), name='update_meter_data'),
    path('meter-data/delete/<int:pk>/', MeterDataDelete.as_view(), name='delete_meter_data'),
    # endregion meter_data

    # region site_management
    path('site/home_page/', SiteHomePage.as_view(), name='home_page_card'),
    path('site/update_robots_and_sitemap/', update_robots_and_sitemap, name='update_robots_and_sitemap'),
    path('site/contact_page/', SiteContactPage.as_view(), name='contact_page_card'),
    path('site/about_page/', SiteAboutPage.as_view(), name='about_page_card'),
    path('site/services_page/', SiteServicesPage.as_view(), name='service_page_card'),
    path('site/services_page/delete/<int:pk>/', DeleteSiteServices.as_view(), name='delete_site_services'),
    path('site/about_page/delte_document/<int:pk>/', DeleteDocument.as_view(), name='delete_document'),
    path('site/about_page/delete_image/<int:pk>/', DeleteGalleryImage.as_view(), name='delete_gallery_image'),
    # endregion site_management

    # region services
    path('services/', ServicesListView.as_view(), name='services'),
    # endregion services

    # region tariffs
    path('tariffs/', TariffListView.as_view(), name='tariffs'),
    path('tariff/<int:pk>/', TariffDetailView.as_view(), name='detail_tariff'),
    path('tariff/create/', TariffCreateView.as_view(), name='create_tariff'),
    path('tariff/create/<int:pk>/', TariffCreateView.as_view(), name='create_copy_tariff'),
    path('tariff/update/<int:pk>/', TariffUpdateView.as_view(), name='update_tariff'),
    path('tariff/delete/<int:pk>/', TariffDelete.as_view(), name='delete_tariff'),
    # endregion tariffs

    # region roles
    path('roles/', RolesUpdateView.as_view(), name='roles'),
    # endregion roles

    # region requisites
    path('requisites/', RequisitesView.as_view(), name='requisites'),
    # endregion requisites

    # region user
    path('users/', UsersListView.as_view(), name='users'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='detail_user'),
    path('user/create/', UserCreateView.as_view(), name='create_user'),
    path('user/update/<int:pk>/', UserUpdateView.as_view(), name='update_user'),
    path('user/delete/<int:pk>/', UserDelete.as_view(), name='delete_user'),
    path('user/profile/<int:pk>/', UserUpdateView.as_view(), name='user_profile'),
    # endregion users

    # region payment_items
    path('payment-items/', PaymentItemsListView.as_view(), name='payment_items'),
    path('payment-items/create/', PaymentItemsCreateView.as_view(), name='create_payment_items'),
    path('payment-items/<int:pk>/', PaymentItemsDetailView.as_view(), name='detail_payment_items'),
    path('payment-items/update/<int:pk>/', PaymentItemsUpdateView.as_view(), name='update_payment_items'),
    path('payment-items/delete/<int:pk>/', PaymentItemsDelete.as_view(), name='delete_payment_items'),
    # endregion payment_items

    # region api_urls
    path('new_users/', new_users, name='new_users'),
    path('load_role/', load_role, name='load_role'),
    path('loading_personal_account_of_owner/', loading_personal_account_of_owner,
         name='loading_personal_account_of_owner'),
    path('loading_services_for_tariff/', loading_services_for_tariff, name='loading_services_for_tariff'),
    path('loading_apartment_of_owner/', loading_apartment_of_owner, name='loading_apartment_of_owner'),
    path('loading_master_of_type_master/', loading_master_of_type_master, name='loading_master_of_type_master'),
    path('loading_floor_section/', loading_floor_section, name='loading_floor_section'),
    path('loading_personal_account/', loading_personal_account, name='loading_personal_account'),
    path('loading_section_for_house/', loading_section_for_house, name='loading_section_for_house'),
    path('loading_apartment_for_section/', loading_apartment_for_section, name='loading_apartment_for_section'),
    path('loading_apartment_for_message/', loading_apartment_for_message, name='loading_apartment_for_message'),
    path('loading_apartment_owner/', loading_apartment_owner, name='loading_apartment_owner'),
    path('check_units/', check_units, name='check_units'),
    path('check_services/', check_services, name='check_services'),
    path('send_invite/', send_invite, name='send_invite'),
    path('loading_unit_for_services/', loading_unit_for_services, name="loading_unit_for_services"),
    path('meter_data_for_receipt/', meter_data_for_receipt, name='meter_data_for_receipt'),
    path('delete_is_checked_receipts/', delete_is_checked_receipts, name='delete_is_checked_receipts'),
    path('delete_is_checked_messages/', delete_is_checked_messages, name='delete_is_checked_messages')
    # endregion api_urls
]
