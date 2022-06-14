from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .task import send_invite_user
from .models import (
    Section, Floor, PersonalAccount, Apartment, House, UnitOfMeasure, Services
)

User = get_user_model()


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
        obj = PersonalAccount.objects.filter(id=pk).values('id', 'number')
        response = {
            'personal_account': list(obj)
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
        is_accounts = True if PersonalAccount.objects.filter(apartment=apartment_id).exists() else False
        owner = Apartment.objects.filter(id=apartment_id).values(
            'owner_id', 'owner__first_name', 'owner__last_name', 'owner__username', 'owner__phone')
        response = {
            'owner': list(owner),
            'is_accounts': is_accounts
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
        service = Services.objects.filter(id=service_id).values('u_measurement__title')
        response = {
            'unit': list(service)
        }
        return JsonResponse(response, status=200)


def send_invite(request):
    if request.is_ajax():
        email = request.GET.get('email')
        role = request.GET.get('role')
        send_invite_user.delay(email, role)
        return JsonResponse({}, status=200)


def initial_house(request):
    if request.is_ajax():
        house = House.objects.all().values('id', 'title')
        response = {
            'house': list(house)
        }
        return JsonResponse(response, status=200)
