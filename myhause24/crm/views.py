from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, formset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView, CreateView
from .models import House, Section, Floor, Apartment, PersonalAccount
from .forms import HouseForm, SectionForm, FloorForm, UserFormSet, OwnerForm, OwnerUpdateForm, \
    ApartmentForm, PersonalAccountForm, InviteOwnerForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .task import send_email


User = get_user_model()


# Create your views here.

# region Houses

class HouseListView(ListView):
    model = House
    template_name = 'crm/pages/houses/list_houses.html'
    context_object_name = 'houses'

    def get_queryset(self):
        return self.model.objects.order_by('id')


class HouseDetailView(DetailView):
    model = House
    template_name = 'crm/pages/houses/detail_house.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super(HouseDetailView, self).get_context_data()
        context['section'] = Section.objects.filter(house=self.object)
        context['floor'] = Floor.objects.filter(house=self.object)
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
            messages.success(self.request, 'Успешно!')
            return super().form_valid(form)
        return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


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
            initial=[{'user': x, 'role': x.role, 'id': x.id} for x in self.object.user.all().order_by('house')],
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
        return self.model.objects.filter(is_staff=False).order_by('id')

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
        return reverse_lazy('detail_owner', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        messages.success(self.request, f"{form.cleaned_data['username']} успешно создан!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class OwnerUpdateView(UpdateView):
    model = User
    template_name = 'crm/pages/owners/update_owner.html'
    form_class = OwnerUpdateForm

    def get_success_url(self):
        return reverse_lazy('detail_owner', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        messages.success(self.request, f'{self.object.email} успешно обновлён!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


class OwnerDelete(DeleteView):
    model = User

    def get_success_url(self):
        messages.success(self.request, f'Владелец  {self.object} удалён!')
        return reverse_lazy('owners')


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
        return self.model.objects.order_by('id').select_related(
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
        messages.success(self.request, f"Квартира №{self.object} успешно создана!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class ApartmentUpdateView(UpdateView):
    model = Apartment
    form_class = ApartmentForm
    success_url = reverse_lazy('apartments')
    template_name = 'crm/pages/apartments/update_apartment.html'

    def get_context_data(self, **kwargs):
        context = super(ApartmentUpdateView, self).get_context_data()
        context['personal_account'] = PersonalAccountForm(
            self.request.POST or None,
            instance=PersonalAccount.objects.get(apartment=self.object),
            prefix='account_form'
        )
        return context

    def get_success_url(self):
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
        messages.success(self.request, f"Квартира №{self.object} успешно обновлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.non_field_errors())
        return super().form_invalid(form)


class ApartmentDelete(DeleteView):
    model = Apartment

    def get_success_url(self):
        messages.success(self.request, f'Квартира  {self.object} удалена!')
        return reverse_lazy('apartments')

# endregion Apartment


# region Accounts

class AccountsListView(ListView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/list_accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return self.model.objects.order_by('id').select_related(
            'apartment'
        )

# endregion Accounts



@login_required(login_url='login')
def index(request):
    return render(request, 'crm/pages/index.html')
