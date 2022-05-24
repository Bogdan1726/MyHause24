from django.http import JsonResponse, HttpResponse
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
