from django.db.models import Q
from crm.models import (
    PersonalAccount, Apartment, CallRequest, Message
)


def get_context(request):
    if request.user.id:
        apartment = Apartment.objects.filter(owner=request.user).select_related(
            'owner', 'house', 'tariff', 'floor', 'section'
        )
        apartment_id = [obj.id for obj in apartment]
        house_id = [obj.house_id for obj in apartment]

        return {
            'list_messages': Message.objects.filter(
                Q(apartment_id__in=apartment_id) | Q(is_all=True) | Q(house_id__in=house_id)
            ).select_related(
                'house', 'section', 'floor', 'apartment', 'apartment__owner', 'sender',
                'sender__role'
            ).order_by('-datetime'),
            'list_apartment': apartment,
            'first_apartment': apartment.first(),
            'apartment': apartment.filter(id=request.GET.get('apartment')).first()
            if request.GET.get('apartment') else None
        }
    return {}
