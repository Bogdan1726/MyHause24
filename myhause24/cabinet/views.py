from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView
from crm.models import PersonalAccount, Apartment

from crm.forms import OwnerUpdateForm

User = get_user_model()

# Create your views here.


class OwnerRequiredMixin(View, AccessMixin):
    """
    Check user is owners
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            messages.error(request, 'Для входа в личный кабинет необходимо авторизоваться')
            return redirect('login')
        if request.user.is_staff:
            messages.error(request, f'Вы вошли в систему как {request.user.username}, '
                                    f'однако у вас недостаточно прав для просмотра личного кабинета')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class SummaryListView(ListView, OwnerRequiredMixin):
    model = PersonalAccount
    template_name = 'cabinet/pages/index.html'


# region Profile

class ProfileDetailView(DetailView, OwnerRequiredMixin):
    model = User
    template_name = 'cabinet/pages/profile/detail_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apartments'] = Apartment.objects.filter(
            owner=self.request.user
        ).select_related(
            'floor', 'section', 'house', 'tariff', 'owner'
        )
        return context


class ProfileUpdateView(UpdateView, OwnerRequiredMixin):
    model = User
    template_name = 'cabinet/pages/profile/update_profile.html'

    def get_form(self, form_class=None):
        if form_class is None:
            return OwnerUpdateForm(self.request.POST or None,
                                   self.request.FILES or None,
                                   instance=self.get_object(),
                                   prefix='profile')

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def get_success_url(self):
        messages.success(self.request, "Ваш профиль успешно обновлён!")
        return reverse_lazy('profile')


# endregion Profile




