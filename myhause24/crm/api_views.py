from django.http import JsonResponse, HttpResponse
from .models import Section, Floor, PersonalAccount, Apartment, House
from django.contrib.auth import get_user_model

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



