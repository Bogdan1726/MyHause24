from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .task import send_invite_user
from .models import (
    Section, Floor, PersonalAccount, Apartment, House, UnitOfMeasure, Services, PriceTariffServices, CashBox, MeterData
)

User = get_user_model()


def new_users(request):
    if request.is_ajax():
        users = User.objects.filter(status='new', is_staff=False).values('id', 'email')
        response = {
            'users': list(users)
        }
        return JsonResponse(response, status=200)


def load_role(request):
    if request.is_ajax():
        user_id = request.GET.get('user')
        role = User.objects.filter(id=user_id).values('role__name')
        response = {
            'role': list(role)
        }
        return JsonResponse(response, status=200)


def loading_floor_section(request):
    if request.is_ajax():
        house_id = request.GET.get('house_id')
        section = Section.objects.filter(house=house_id).values('id', 'title')
        floor = Floor.objects.filter(house=house_id).values('id', 'title')
        response = {
            'section': list(section),
            'floor': list(floor)
        }
        return JsonResponse(response, status=200)


def loading_personal_account(request):
    if request.is_ajax():
        pk = request.GET.get('id')
        obj = PersonalAccount.objects.filter(id=pk).values(
            'id', 'number', 'apartment', 'apartment__house', 'apartment__section', 'apartment__section__title',
            'apartment__tariff', 'apartment__number', 'apartment__owner__first_name',
            'apartment__owner__last_name', 'apartment__owner__username', 'apartment__owner__phone'
        )
        response = {
            'personal_account': list(obj),
        }
        return JsonResponse(response, status=200)


def loading_section_for_house(request):
    if request.is_ajax():
        house_id = request.GET.get('house_id')
        section = Section.objects.filter(house=house_id).values('id', 'title')
        response = {
            'section': list(section)
        }
        return JsonResponse(response, status=200)


def loading_apartment_for_section(request):
    if request.is_ajax():
        section_id = request.GET.get('section_id')
        apartment = Apartment.objects.filter(section=section_id).values(
            'id', 'number')
        response = {
            'apartment': list(apartment)
        }
        return JsonResponse(response, status=200)


def loading_apartment_owner(request):
    if request.is_ajax():
        apartment_id = request.GET.get('apartment_id')
        tariff = Apartment.objects.filter(id=apartment_id).values('tariff_id', 'tariff__title')
        personal_account = PersonalAccount.objects.filter(apartment=apartment_id).values(
            'id', 'number'
        )
        is_accounts = True if PersonalAccount.objects.filter(apartment=apartment_id).exists() else False
        owner = Apartment.objects.filter(id=apartment_id).values(
            'owner_id', 'owner__first_name', 'owner__last_name', 'owner__username', 'owner__phone')
        response = {
            'owner': list(owner),
            'is_accounts': is_accounts,
            'tariff': list(tariff),
            'personal_account': list(personal_account)
        }
        return JsonResponse(response, status=200)


def check_units(request):
    if request.is_ajax():
        unit = request.GET.get('value')
        obj = get_object_or_404(UnitOfMeasure, title=unit)
        services = True if Services.objects.filter(u_measurement=obj).exists() else False
        response = {
            'is_services': services
        }
        return JsonResponse(response, status=200)


def loading_unit_for_services(request):
    if request.is_ajax():
        service_id = request.GET.get('service_id')
        tariff_id = request.GET.get('tariff_id')
        services_price = 0
        if service_id and tariff_id:
            price = PriceTariffServices.objects.filter(services=service_id, tariff=tariff_id).first()
            services_price += price.price if price else services_price
        service = Services.objects.filter(id=service_id).values('u_measurement__title')
        response = {
            'unit': list(service),
            'services_price': services_price
        }
        return JsonResponse(response, status=200)


def send_invite(request):
    if request.is_ajax():
        email = request.GET.get('email')
        role = request.GET.get('role')
        send_invite_user.delay(email, role)
        return JsonResponse({}, status=200)


def loading_apartment_of_owner(request):
    if request.is_ajax():
        owner_id = request.GET.get('owner_id')
        apartments = Apartment.objects.filter(owner=owner_id).values('id', 'house__title', 'number')
        response = {
            'apartments': list(apartments)
        }
        return JsonResponse(response, status=200)


def loading_master_of_type_master(request):
    if request.is_ajax():
        role_id = request.GET.get('role_id')
        masters = User.objects.filter(role=role_id).values('id', 'email', 'first_name', 'last_name', 'role__name')
        response = {
            'masters': list(masters)
        }
        return JsonResponse(response, status=200)


def loading_personal_account_of_owner(request):
    if request.is_ajax():
        owner_id = request.GET.get('owner_id')
        apartments = [obj.id for obj in Apartment.objects.filter(owner=owner_id)]
        personal_account = PersonalAccount.objects.filter(apartment_id__in=apartments).values(
            'id', 'number'
        )
        response = {
            'personal_account': list(personal_account)
        }
        return JsonResponse(response, status=200)


def loading_services_for_tariff(request):
    if request.is_ajax():
        tariff_id = request.GET.get('tariff_id')
        services = PriceTariffServices.objects.filter(tariff=tariff_id).values(
            'services', 'price', 'services__u_measurement__title'
        )
        response = {
            'services': list(services)
        }
        return JsonResponse(response, status=200)


def meter_data_for_receipt(request):
    if request.is_ajax():
        service_id = request.GET.get('service_id')
        apartment_id = request.GET.get('apartment_id')
        meter_data = MeterData.objects.filter(apartment_id=apartment_id, counter_id=service_id, status='new')
        indications = 0
        if meter_data.exists():
            indications += meter_data.last().indications
        response = {
            'indications': indications
        }
        return JsonResponse(response, status=200)
