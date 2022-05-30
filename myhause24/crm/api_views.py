from django.http import JsonResponse, HttpResponse
from .models import Section, Floor, PersonalAccount
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
    return HttpResponse()


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
    return HttpResponse()


def loading_personal_account(request):
    if request.is_ajax():
        pk = request.GET.get('id')
        obj = PersonalAccount.objects.filter(id=pk).values('id', 'number')
        response = {
            'personal_account': list(obj)
        }
        return JsonResponse(response, status=200)
    return HttpResponse()
