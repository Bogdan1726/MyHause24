from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .task import send_email
import random
from user.models import Role
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView, CreateView
from .models import (
    House, Section, Floor, Apartment, PersonalAccount, Services, UnitOfMeasure,
    Tariff, PriceTariffServices, Requisites)
from .forms import (
    HouseForm, SectionForm, FloorForm, UserFormSet, OwnerForm, OwnerUpdateForm,
    ApartmentForm, PersonalAccountForm, InviteOwnerForm, AccountsForm, UnitOfMeasureForm,
    ServicesForm, TariffForm, PriceTariffServicesForm, RolesForm, RequisitesForm,
    UserAdminForm
)

User = get_user_model()


# Create your views here.

# region Houses

class HouseListView(ListView):
    model = House
    template_name = 'crm/pages/houses/list_houses.html'
    context_object_name = 'houses'

    def get_queryset(self):
        return self.model.objects.order_by('-id')


class HouseDetailView(DetailView):
    model = House
    template_name = 'crm/pages/houses/detail_house.html'
    context_object_name = 'house'

    def get_queryset(self):
        return self.model.objects.prefetch_related('user__role')

    def get_context_data(self, **kwargs):
        context = super(HouseDetailView, self).get_context_data()
        context['section'] = Section.objects.filter(house=self.object).select_related('house')
        context['floor'] = Floor.objects.filter(house=self.object).select_related('house')
        return context


class BaseHouseView(SingleObjectTemplateResponseMixin, ModelFormMixin, ProcessFormView):
    model = House
    form_class = HouseForm
    formset_for_section = modelformset_factory(Section, form=SectionForm, extra=0, can_delete=True)
    formset_for_floor = modelformset_factory(Floor, form=FloorForm, extra=0, can_delete=True)
    formset_for_user = formset_factory(form=UserFormSet, extra=0, can_delete=True)

    def get_object(self, queryset=None):
        try:
            return super().get_object()
        except AttributeError:
            return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        if self.request.resolver_match.url_name == 'update_house':
            messages.success(self.request, f'Дом {self.object} обновлён!')
        else:
            messages.success(self.request, f'Дом {self.object} создан!')
        return reverse_lazy('detail_house', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        formset_for_section = context['formset_for_section']
        formset_for_floor = context['formset_for_floor']
        formset_for_user = context['formset_for_user']
        if formset_for_section.is_valid() and formset_for_floor.is_valid() and formset_for_user.is_valid():
            house = form.save()
            for section in formset_for_section:
                if section.cleaned_data:
                    if section.is_valid():
                        section = section.save(commit=False)
                        section.house = house
                        section.save()
            formset_for_section.save()
            for floor in formset_for_floor:
                if floor.cleaned_data:
                    if floor.is_valid():
                        floor = floor.save(commit=False)
                        floor.house = house
                        floor.save()
            formset_for_floor.save()
            house.user.clear()
            for form_user in formset_for_user:
                if form_user.cleaned_data and form_user.cleaned_data['DELETE'] is False:
                    user = form_user.cleaned_data.get('user')
                    house.user.add(user)
            return super().form_valid(form)
        return self.form_invalid(form)


class HouseUpdateView(BaseHouseView):
    template_name = 'crm/pages/houses/update_house.html'

    def get_context_data(self, **kwargs):
        context = super(HouseUpdateView, self).get_context_data()
        context['formset_for_section'] = self.formset_for_section(
            self.request.POST or None,
            queryset=Section.objects.filter(house=self.object),
            prefix='section'
        )
        context['formset_for_floor'] = self.formset_for_floor(
            self.request.POST or None,
            queryset=Floor.objects.filter(house=self.object),
            prefix='floor'
        )
        context['formset_for_user'] = self.formset_for_user(
            self.request.POST or None,
            initial=[
                {
                    'user': x,
                    'role': x.role,
                    'id': x.id
                }
                for x in self.object.user.all().select_related('role').order_by('house')
            ],
            prefix='user'
        )
        return context


class HouseCreateView(BaseHouseView):
    template_name = 'crm/pages/houses/create_house.html'

    def get_context_data(self, **kwargs):
        context = super(HouseCreateView, self).get_context_data()
        context['formset_for_section'] = self.formset_for_section(
            self.request.POST or None,
            queryset=Section.objects.none(),
            prefix='section'
        )
        context['formset_for_floor'] = self.formset_for_floor(
            self.request.POST or None,
            queryset=Floor.objects.none(),
            prefix='floor'
        )
        context['formset_for_user'] = self.formset_for_user(
            self.request.POST or None,
            prefix='user'
        )
        return context


class HouseDelete(DeleteView):
    model = House

    def get_success_url(self):
        messages.success(self.request, f'Дом  {self.object} удалён!')
        return reverse_lazy('houses')


# endregion Houses

# region Owners


class OwnerListView(ListView):
    model = User
    template_name = 'crm/pages/owners/list_owners.html'
    context_object_name = 'owners'

    def get_queryset(self):
        return self.model.objects.filter(is_staff=False).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(OwnerListView, self).get_context_data()
        context['apartments'] = Apartment.objects.all().select_related(
            'section', 'house', 'floor', 'tariff', 'house', 'owner')
        return context


class OwnerDetailView(DetailView):
    model = User
    template_name = 'crm/pages/owners/detail_owner.html'
    context_object_name = 'owner'

    def get_context_data(self, **kwargs):
        context = super(OwnerDetailView, self).get_context_data()
        context['apartments'] = Apartment.objects.all().select_related(
            'section', 'house', 'floor', 'tariff', 'house', 'owner')
        context['personal_account'] = PersonalAccount.objects.all().select_related(
            'apartment')
        return context


class OwnerCreateView(CreateView):
    model = User
    template_name = 'crm/pages/owners/create_owner.html'
    form_class = OwnerForm

    def get_success_url(self):
        messages.success(self.request, f"{self.object.username} успешно создан!")
        return reverse_lazy('detail_owner', kwargs={'pk': self.object.id})


class OwnerUpdateView(UpdateView):
    model = User
    template_name = 'crm/pages/owners/update_owner.html'
    form_class = OwnerUpdateForm

    def get_success_url(self):
        messages.success(self.request, f'{self.object.username} успешно обновлён!')
        return reverse_lazy('detail_owner', kwargs={'pk': self.object.id})


class OwnerDelete(DeleteView):
    model = User

    def get_success_url(self):
        messages.success(self.request, f'Владелец  {self.object} удалён!')
        return reverse_lazy('owners')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if Apartment.objects.filter(owner=self.object).exists():
            messages.error(request, 'Нельзя удалить владельца, за которым закреплена квартира')
            return HttpResponseRedirect(reverse_lazy('owners'))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


def invite_owner(request):
    if request.method == 'POST':
        messages.success(request, 'Приглашение отправлено')
        send_email.delay(request.POST['email'])
    context = {
        'form': InviteOwnerForm(request.POST or None)
    }
    return render(request, 'crm/pages/owners/invite_owner.html', context)


# endregion Owners

# region Apartment

class ApartmentListView(ListView):
    model = Apartment
    template_name = 'crm/pages/apartments/list_apartments.html'
    context_object_name = 'apartments'

    def get_queryset(self):
        return self.model.objects.order_by('-id').select_related(
            'section', 'floor', 'house', 'owner', 'tariff'
        )


class ApartmentDetailView(DetailView):
    model = Apartment
    template_name = 'crm/pages/apartments/detail_apartment.html'
    context_object_name = 'apartment'

    def get_queryset(self):
        return self.model.objects.select_related(
            'section', 'floor', 'house', 'owner', 'tariff'
        )

    def get_context_data(self, **kwargs):
        context = super(ApartmentDetailView, self).get_context_data()
        context['personal_account'] = PersonalAccount.objects.filter(apartment=self.object).select_related(
            'apartment'
        ).first()
        return context


class ApartmentCreateView(CreateView):
    model = Apartment
    form_class = ApartmentForm
    success_url = reverse_lazy('apartments')
    template_name = 'crm/pages/apartments/create_apartment.html'

    def get_context_data(self, **kwargs):
        context = super(ApartmentCreateView, self).get_context_data()
        context['personal_account'] = PersonalAccountForm(
            self.request.POST or None,
            prefix='account_form'
        )
        return context

    def get_success_url(self):
        messages.success(self.request, f"Квартира №{self.object.number} успешно создана!")
        if 'action_save' in self.request.POST:
            return reverse_lazy('detail_apartment', kwargs={'pk': self.object.id})
        return reverse_lazy('create_apartment')

    def form_valid(self, form):
        context = self.get_context_data()
        personal_account = context['personal_account']
        account = PersonalAccount.objects.all()
        if personal_account.is_valid():
            try:
                obj = account.get(number=personal_account.cleaned_data['number'])
                if obj.apartment:
                    messages.error(self.request, 'К этому лицевому счету уже закреплена квартира')
                    return super().form_invalid(form)
                self.object = form.save()
                account.filter(number=personal_account.cleaned_data['number']).update(
                    apartment=self.object
                )
            except PersonalAccount.DoesNotExist:
                self.object = form.save()
                account.create(
                    number=personal_account.cleaned_data['number'],
                    apartment=self.object
                )
        return super().form_valid(form)


class ApartmentUpdateView(UpdateView):
    model = Apartment
    form_class = ApartmentForm
    success_url = reverse_lazy('apartments')
    template_name = 'crm/pages/apartments/update_apartment.html'

    def get_context_data(self, **kwargs):
        context = super(ApartmentUpdateView, self).get_context_data()
        context['personal_account'] = PersonalAccountForm(
            self.request.POST or None,
            instance=PersonalAccount.objects.filter(apartment=self.object).first(),
            prefix='account_form'
        )
        return context

    def get_success_url(self):
        messages.success(self.request, f"Квартира №{self.object} успешно обновлена!")
        if 'action_save' in self.request.POST:
            return reverse_lazy('detail_apartment', kwargs={'pk': self.object.id})
        return reverse_lazy('create_apartment')

    def form_valid(self, form):
        context = self.get_context_data()
        personal_account = context['personal_account']
        account = PersonalAccount.objects.all()
        if personal_account.is_valid():
            try:
                obj = account.get(number=personal_account.cleaned_data['number'])
                if obj.apartment and obj.apartment != self.object:
                    messages.error(self.request, 'К этому лицевому счету уже закреплена квартира')
                    return super().form_invalid(form)
                account.filter(apartment=self.object).update(apartment=None)
                account.filter(
                    number=personal_account.cleaned_data['number']
                ).update(apartment=self.object)

            except PersonalAccount.DoesNotExist:
                account.filter(apartment=self.object).update(apartment=None)
                account.create(
                    number=personal_account.cleaned_data['number'],
                    apartment=self.object
                )
        return super().form_valid(form)


class ApartmentDelete(DeleteView):
    model = Apartment

    def get_success_url(self):
        messages.success(self.request, f'Квартира №{self.object.number} удалена!')
        return reverse_lazy('apartments')


# endregion Apartment

# region Accounts

class AccountsListView(ListView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/list_accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return self.model.objects.order_by('-id').select_related(
            'apartment', 'apartment__house', 'apartment__section', 'apartment__owner'
        )


class AccountsDetailView(DeleteView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/detail_accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return self.model.objects.select_related(
            'apartment', 'apartment__house', 'apartment__section', 'apartment__owner'
        )


class AccountsCreateView(CreateView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/create_accounts.html'

    def get_success_url(self):
        messages.success(self.request, f'Лицевой счет №{self.object.number} создан!')
        return reverse_lazy('detail_accounts', kwargs={'pk': self.object.id})

    def generate_number(self):
        while True:
            random_number = f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}"
            if not self.model.objects.filter(number=random_number).exists():
                return random_number

    def get_form(self, form_class=None):
        if form_class is None:
            return AccountsForm(self.request.POST or None,
                                initial={'number': self.generate_number()})


class AccountsUpdateView(UpdateView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/update_accounts.html'

    def get_success_url(self):
        messages.success(self.request, f'Лицевой счет №{self.object.number} обновлён!')
        return reverse_lazy('detail_accounts', kwargs={'pk': self.object.id})

    def get_form(self, form_class=None):
        if form_class is None:
            if self.object.apartment:
                return AccountsForm(self.request.POST or None,
                                    instance=self.object,
                                    initial={'house': self.object.apartment.house_id,
                                             'section': self.object.apartment.section_id})
            return AccountsForm(self.request.POST or None, instance=self.object)


class AccountsDelete(DeleteView):
    model = PersonalAccount

    def get_success_url(self):
        messages.success(self.request, f'Лицевой счет №{self.object} удалён!')
        return reverse_lazy('accounts')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.apartment:
            messages.error(request, 'К данному Лицевому счету закреплена квартира')
            return HttpResponseRedirect(reverse_lazy('accounts'))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# endregion Accounts

# region Services

class ServicesListView(CreateView):
    model = Services
    template_name = 'crm/pages/services/list_services.html'
    formset_for_services = modelformset_factory(Services, form=ServicesForm, extra=0, can_delete=True)
    formset_for_unit = modelformset_factory(UnitOfMeasure, form=UnitOfMeasureForm, extra=0, can_delete=True)

    def get_success_url(self):
        messages.success(self.request, 'Услуги обновлены')
        return reverse_lazy('services')

    def get_form(self, form_class=None):
        if form_class is None:
            return self.formset_for_services(self.request.POST or None,
                                             queryset=self.model.objects.all().select_related(
                                                 'u_measurement'
                                             ),
                                             prefix='services')

    def get_context_data(self, **kwargs):
        context = super(ServicesListView, self).get_context_data()
        context['form_unit'] = self.formset_for_unit(self.request.POST or None,
                                                     queryset=UnitOfMeasure.objects.all(),
                                                     prefix='unit')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form_unit = context['form_unit']
        if form_unit.is_valid():
            for forms in form_unit:
                if forms.cleaned_data:
                    if forms.is_valid():
                        forms.save()
            form_unit.save()
            return super().form_valid(form)
        messages.error(self.request, form_unit.errors)
        return self.form_invalid(form)


# endregion Services

# region Tariffs


class TariffListView(ListView):
    model = Tariff
    template_name = 'crm/pages/tariffs/list_tariffs.html'
    context_object_name = 'tariffs'

    def get_queryset(self):
        return self.model.objects.all().order_by('-id')


class TariffDetailView(DetailView):
    model = Tariff
    template_name = 'crm/pages/tariffs/detail_tariff.html'
    context_object_name = 'tariff'

    def get_context_data(self, **kwargs):
        context = super(TariffDetailView, self).get_context_data()
        context['services_price'] = PriceTariffServices.objects.filter(tariff=self.object)
        return context


class TariffCreateView(CreateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'crm/pages/tariffs/create_tariff.html'
    formset_for_services_price = modelformset_factory(
        PriceTariffServices, form=PriceTariffServicesForm, extra=0, can_delete=True
    )

    def get_form(self, form_class=None):
        if form_class is None:
            if self.kwargs.get('pk'):
                obj = get_object_or_404(Tariff, id=self.kwargs.get('pk'))
                return TariffForm(self.request.POST or None,
                                  initial={
                                      'title': obj.title,
                                      'description': obj.description
                                  })
            return TariffForm(self.request.POST or None)

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} создан!')
        return reverse_lazy('detail_tariff', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        obj = False
        price_tariff_services = PriceTariffServices.objects.all().select_related(
            'services', 'tariff'
        )
        if self.kwargs.get('pk'):
            obj = get_object_or_404(Tariff, id=self.kwargs.get('pk'))
            count_form = price_tariff_services.filter(tariff=obj).count()
            self.formset_for_services_price = modelformset_factory(
                PriceTariffServices, form=PriceTariffServicesForm, extra=count_form, can_delete=True
            )
        context = super(TariffCreateView, self).get_context_data()
        context['formset'] = self.formset_for_services_price(
            self.request.POST or None,
            queryset=PriceTariffServices.objects.none(),
            initial=[
                {'services': obj.services,
                 'price': obj.price,
                 'unit': obj.services.u_measurement
                 }
                for obj in price_tariff_services.filter(tariff=obj)
            ] if obj else None,
            prefix='services_price'
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        if formset.is_valid():
            for forms in formset:
                if forms.cleaned_data and forms.cleaned_data['DELETE'] is False:
                    if forms.is_valid():
                        services_price = forms.save(commit=False)
                        services_price.tariff = self.object
                        services_price.save()
            formset.save()
            return super().form_valid(form)
        messages.error(self.request, formset.errors)
        return self.form_invalid(form)


class TariffUpdateView(UpdateView):
    model = Tariff
    form_class = TariffForm
    template_name = 'crm/pages/tariffs/update_tariff.html'
    formset_for_services_price = modelformset_factory(
        PriceTariffServices, form=PriceTariffServicesForm, extra=0, can_delete=True
    )

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} обновлён!')
        return reverse_lazy('detail_tariff', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super(TariffUpdateView, self).get_context_data()
        context['formset'] = self.formset_for_services_price(
            self.request.POST or None,
            queryset=PriceTariffServices.objects.filter(tariff=self.object).select_related(
                'tariff', 'services', 'services__u_measurement'
            ),
            prefix='services_price',
        )

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        self.object = form.save()
        if formset.is_valid():
            for forms in formset:
                if forms.cleaned_data and forms.cleaned_data['DELETE'] is False:
                    if forms.is_valid():
                        services_price = forms.save(commit=False)
                        services_price.tariff = self.object
                        services_price.save()
            formset.save()
            return super().form_valid(form)
        messages.error(self.request, formset.errors)
        return self.form_invalid(form)


class TariffDelete(DeleteView):
    model = Tariff

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} удалён!')
        return reverse_lazy('tariffs')


# endregion Tariffs

# region Roles

class RolesUpdateView(CreateView):
    model = Role
    template_name = 'crm/pages/roles.html'
    formset_for_role = modelformset_factory(Role, form=RolesForm, extra=0)

    def get_form(self, form_class=None):
        if form_class is None:
            return self.formset_for_role(self.request.POST or None,
                                         queryset=self.model.objects.all(),
                                         prefix='roles')

    def get_success_url(self):
        messages.success(self.request, 'Роли обновлены')
        return reverse_lazy('roles')


# endregion Roles


# region Requisites

class RequisitesView(UpdateView):
    model = Requisites
    form_class = RequisitesForm
    template_name = 'crm/pages/requisites.html'

    def get_success_url(self):
        messages.success(self.request, 'Платежные реквизиты обновлены')
        return reverse_lazy('requisites')

    def get_object(self, queryset=None):
        requisites = Requisites.objects.get_or_create(
            id=1
        )
        obj = Requisites.objects.get(id=1)
        return obj


# endregion Requisites

# region Users

class UsersListView(ListView):
    model = User
    template_name = 'crm/pages/users/list_users.html'
    context_object_name = 'users'

    def get_queryset(self):
        return self.model.objects.filter(is_staff=True).order_by('role').select_related('role')


class UserDetailView(DetailView):
    model = User
    template_name = 'crm/pages/users/detail_user.html'
    context_object_name = 'user'

    def get_queryset(self):
        return self.model.objects.select_related('role')


class UserCreateView(CreateView):
    model = User
    form_class = UserAdminForm
    template_name = 'crm/pages/users/create_user.html'

    def get_success_url(self):
        messages.success(self.request, f"{self.object} успешно создан!")
        return reverse_lazy('detail_user', kwargs={'pk': self.object.id})


class UserUpdateView(UpdateView):
    model = User
    form_class = UserAdminForm
    template_name = 'crm/pages/users/update_user.html'

    def get_success_url(self):
        messages.success(self.request, f"{self.object} успешно обновлён!")
        return reverse_lazy('detail_user', kwargs={'pk': self.object.id})


class UserDelete(DeleteView):
    model = User

    def get_success_url(self):
        messages.success(self.request, f'{self.object} удалён!')
        return reverse_lazy('users')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_superuser:
            messages.error(request, f'{self.object} является супер пользователем и не может быть удалён')
            return HttpResponseRedirect(reverse_lazy('users'))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

# endregion Users

@login_required(login_url='login')
def index(request):
    return render(request, 'crm/pages/index.html')
