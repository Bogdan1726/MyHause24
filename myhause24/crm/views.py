import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, FloatField, Q
from django.db.models.functions import Coalesce, Cast, Greatest
from django.forms import modelformset_factory, formset_factory
from django.shortcuts import render
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import get_user_model
from openpyxl.writer.excel import save_virtual_workbook

from .services.xlsx_services import write_to_file
from .task import send_email, send_receipt_for_owner
import random
from user.models import Role
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView, CreateView
from .models import (
    House, Section, Floor, Apartment, PersonalAccount, Services, UnitOfMeasure,
    Tariff, PriceTariffServices, Requisites, PaymentItems, MeterData, CallRequest,
    CashBox, Receipt, CalculateReceiptService, ReceiptTemplate, Requisites,
    Message
)
from .forms import (
    HouseForm, SectionForm, FloorForm, UserFormSet, OwnerForm, OwnerUpdateForm,
    ApartmentForm, PersonalAccountForm, InviteOwnerForm, AccountsForm, UnitOfMeasureForm,
    ServicesForm, TariffForm, PriceTariffServicesForm, RolesForm, RequisitesForm,
    UserAdminForm, UserAdminChangeForm, PaymentItemsForm, MeterDataForm, MasterCallForm,
    CashBoxForm, ReceiptForm, CalculateReceiptServiceForm, SettingsTemplatesForm, MessageForm
)

User = get_user_model()


# Create your views here.

# region Statistics
@login_required(login_url='login')
def index(request):
    return render(request, 'crm/pages/index.html')


def get_balance_cash():
    cash = CashBox.objects.all()
    cash_income = cash.filter(status=True, type=True).aggregate(sum=Sum('sum'))
    cash_expense = cash.filter(status=True, type=False).aggregate(sum=Sum('sum'))
    cash_balance = 0

    income = cash_income['sum']
    expense = cash_expense['sum']
    if income is not None:
        cash_balance += income
    if expense is not None:
        cash_balance -= expense

    return cash_balance


def get_balance_account():
    account_balance = 0
    account_debit = 0

    queryset = PersonalAccount.objects.select_related(
        'apartment', 'apartment__house', 'apartment__section', 'apartment__owner'
    ).annotate(
        balance=
        Greatest(Sum('cash_account__sum', filter=Q(cash_account__status=True), distinct=True), Decimal(0))
        -
        Greatest(Sum('receipt_account__sum', filter=Q(receipt_account__status=True), distinct=True), Decimal(0))
    ).order_by('-id')

    for obj in queryset:
        if obj.balance < 0:
            account_debit += obj.balance
        elif obj.balance > 0:
            account_balance += obj.balance
    return [str(account_debit).replace('-', ''), account_balance]


# endregion Statistics

# region CashBox

class CashBoxListView(ListView):
    model = CashBox
    template_name = 'crm/pages/cash_box/list_cash_box.html'
    context_object_name = 'cash_box'

    def get_queryset(self):
        account_id = self.request.GET.get('account', None)
        if account_id:
            return self.model.objects.filter(personal_account=account_id).select_related(
                'owner', 'manager', 'payment_items', 'personal_account', 'receipt').order_by('-date', '-id')
        return self.model.objects.all().select_related(
            'owner', 'manager', 'payment_items', 'personal_account', 'receipt').order_by('-date', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cash_balance'] = get_balance_cash()
        context['account_balance'] = get_balance_account()[1]
        context['account_debit'] = get_balance_account()[0]
        return context


class CashBoxDetailView(DetailView):
    model = CashBox
    template_name = 'crm/pages/cash_box/detail_cash_box.html'
    context_object_name = 'cash_box'

    def get_queryset(self):
        return self.model.objects.select_related(
            'owner', 'manager', 'payment_items', 'personal_account', 'receipt')


class CashBoxCreateView(CreateView):
    model = CashBox
    template_name = 'crm/pages/cash_box/create_cash_box.html'

    def get_success_url(self):
        messages.success(self.request, f'Ведомость №{self.object.number} добавлена!')
        return reverse_lazy('cash_box')

    def generate_number(self):
        """
        Returns the number for the initial form CashBox
        """
        counter = 1
        while True:
            try:
                obj_id = self.model.objects.order_by('-id').first().id
            except AttributeError:
                obj_id = 0
            number = f'{obj_id + counter:010}'
            if not self.model.objects.filter(number=number).exists():
                return number
            counter += 1

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            cash_id = self.request.GET.get('cash', None)
            account_id = self.request.GET.get('account', None)
            if cash_id:
                obj = get_object_or_404(CashBox, id=cash_id)
                return CashBoxForm(self.request.POST or None,
                                   initial={'number': self.generate_number(),
                                            'manager': obj.manager_id,
                                            'date': obj.date,
                                            'sum': obj.sum,
                                            'owner': obj.owner_id,
                                            'comment': obj.comment,
                                            'payment_items': obj.payment_items_id,
                                            'personal_account': obj.personal_account_id,
                                            'type_pay': self.request.GET.get('type_pay')})
            if account_id:
                obj = get_object_or_404(PersonalAccount, id=account_id)
                return CashBoxForm(self.request.POST or None,
                                   initial={'number': self.generate_number(),
                                            'owner': obj.apartment.owner_id,
                                            'personal_account': obj.id,
                                            'type_pay': 'income'})
            return CashBoxForm(self.request.POST or None,
                               initial={'number': self.generate_number(),
                                        'manager': self.request.user.id,
                                        'type_pay': self.request.GET.get('type_pay')})

    def form_valid(self, form):
        if self.request.GET.get('type_pay') == 'expense':
            cash = form.save(commit=False)
            cash.type = False
            cash.save()
        return super().form_valid(form)


class CashBoxUpdateView(UpdateView):
    model = CashBox
    template_name = 'crm/pages/cash_box/update_cash_box.html'

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            return CashBoxForm(self.request.POST or None,
                               instance=self.object,
                               initial={
                                   'manager': self.object.manager_id,
                                   'owner': self.object.owner_id,
                                   'personal_account': self.object.personal_account_id,
                                   'type_pay': 'income' if self.object.type else 'expense'})

    def get_success_url(self):
        messages.success(self.request, f'Ведомость №{self.object.number} обновлена!')
        return reverse_lazy('cash_box')


class CashBoxDelete(DeleteView):
    model = CashBox

    def get_success_url(self):
        messages.success(self.request, f'Платеж №{self.object.number} удален!')
        return reverse_lazy('cash_box')


# endregion CashBox

# region Receipts


class ReceiptListView(ListView):
    model = Receipt
    template_name = 'crm/pages/receipts/list_receipts.html'
    context_object_name = 'receipts'

    def get_queryset(self):
        account_id = self.request.GET.get('account', None)
        if account_id:
            return self.model.objects.filter(personal_account_id=account_id).select_related(
                'tariff', 'apartment', 'apartment__owner', 'apartment__house'
            ).order_by('-date', '-id')
        return self.model.objects.all().select_related(
            'tariff', 'apartment', 'apartment__owner', 'apartment__house'
        ).order_by('-date', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cash_balance'] = get_balance_cash()
        context['account_balance'] = get_balance_account()[1]
        context['account_debit'] = get_balance_account()[0]
        return context


class ReceiptDetailView(DetailView):
    model = Receipt
    template_name = 'crm/pages/receipts/detail_receipt.html'
    context_object_name = 'receipt'

    def get_queryset(self):
        return self.model.objects.select_related(
            'tariff', 'apartment', 'apartment__owner', 'apartment__house', 'apartment__section')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['personal_account'] = PersonalAccount.objects.filter(apartment=self.object.apartment_id).first()
        context['services'] = CalculateReceiptService.objects.filter(receipt=self.object).select_related(
            'services', 'services__u_measurement', 'receipt')
        context['sum'] = context['services'].aggregate(sum=Sum('cost'))
        return context


class ReceiptCreateView(CreateView):
    model = Receipt
    template_name = 'crm/pages/receipts/create_receipt.html'
    formset_for_services = modelformset_factory(
        CalculateReceiptService, form=CalculateReceiptServiceForm, extra=0, can_delete=True)

    def get_success_url(self):
        messages.success(self.request, f'Квитанция №{self.object.number} добавлена!')
        return reverse_lazy('receipts')

    def generate_number(self):
        """
        Returns the number for the initial form data
        """
        counter = 1
        while True:
            try:
                obj_id = self.model.objects.order_by('-id').first().id
            except AttributeError:
                obj_id = 0
            number = f'{obj_id + counter:08}'
            if not self.model.objects.filter(number=number).exists():
                return number
            counter += 1

    def get_form(self, form_class=None):
        if form_class is None:
            receipt_id = self.request.GET.get('receipt_id', None)
            account_id = self.request.GET.get('account', None)
            if receipt_id:
                obj = Receipt.objects.filter(id=receipt_id).select_related(
                    'apartment', 'tariff').first()
                personal_account = PersonalAccount.objects.filter(
                    apartment=obj.apartment_id).select_related('apartment').first()
                return ReceiptForm(self.request.POST or None,
                                   initial={'number': self.generate_number(),
                                            'date': obj.date,
                                            'status': obj.status,
                                            'status_pay': obj.status_pay,
                                            'tariff': obj.tariff_id,
                                            'date_start': obj.date_start,
                                            'date_end': obj.date_end,
                                            'house': obj.apartment.house_id,
                                            'section': obj.apartment.section_id,
                                            'apartment': obj.apartment_id,
                                            'personal_accounts': personal_account.id if personal_account else None})
            if account_id:
                obj = get_object_or_404(PersonalAccount, id=account_id)
                return ReceiptForm(self.request.POST or None,
                                   initial={'number': self.generate_number(),
                                            'tariff': obj.apartment.tariff_id,
                                            'house': obj.apartment.house_id,
                                            'section': obj.apartment.section_id,
                                            'apartment': obj.apartment_id,
                                            'personal_accounts': obj.id})
            return ReceiptForm(self.request.POST or None,
                               initial={'number': self.generate_number()})

    def get_context_data(self, **kwargs):
        obj = False
        receipt_id = self.request.GET.get('receipt_id', None)
        account_id = self.request.GET.get('account', None)

        calculate_receipt_service = CalculateReceiptService.objects.all().select_related(
            'services', 'receipt', 'services__u_measurement'
        )
        context = super(ReceiptCreateView, self).get_context_data()

        if receipt_id:
            obj = get_object_or_404(Receipt, id=receipt_id)
            count_form = calculate_receipt_service.filter(receipt=obj).count()
            self.formset_for_services = modelformset_factory(
                CalculateReceiptService, form=CalculateReceiptServiceForm, extra=count_form, can_delete=True)
            context['owner_data'] = Apartment.objects.filter(id=obj.apartment_id).select_related(
                'owner'
            ).first()
        context['formset_for_services'] = self.formset_for_services(
            self.request.POST or None,
            queryset=CalculateReceiptService.objects.none(),
            initial=[
                {'services': obj.services,
                 'price': obj.price,
                 'quantity': obj.quantity,
                 'cost': obj.cost,
                 'unit': obj.services.u_measurement}
                for obj in calculate_receipt_service.filter(receipt=obj)
            ] if obj else None,
            prefix='services',
        )
        context['meter_data'] = MeterData.objects.select_related(
            'apartment', 'apartment__house', 'apartment__section', 'counter', 'counter__u_measurement'
        ).order_by('-id')

        if account_id:
            obj = get_object_or_404(PersonalAccount, id=account_id)
            context['owner_data'] = Apartment.objects.filter(id=obj.apartment_id).select_related(
                'owner'
            ).first()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset_for_services = context['formset_for_services']
        personal_account = get_object_or_404(PersonalAccount, id=form.cleaned_data['personal_accounts'])
        self.object = form.save(commit=False)
        self.object.personal_account = personal_account
        self.object.save()
        sum = 0
        if formset_for_services.is_valid():
            for forms in formset_for_services:
                if forms.cleaned_data and forms.cleaned_data['DELETE'] is False:
                    if forms.is_valid():
                        services = forms.save(commit=False)
                        services.receipt = self.object
                        services.save()
                        sum += services.cost
                    else:
                        Receipt.objects.get(id=self.object.id).delete()
            formset_for_services.save()
            sum_save = form.save(commit=False)
            sum_save.sum = sum
            sum_save.save()
            return super().form_valid(form)
        Receipt.objects.get(id=self.object.id).delete()
        messages.error(self.request, formset_for_services.errors)
        return self.form_invalid(form)


class ReceiptUpdateView(UpdateView):
    model = Receipt
    template_name = 'crm/pages/receipts/update_receipt.html'
    formset_for_services = modelformset_factory(
        CalculateReceiptService, form=CalculateReceiptServiceForm, extra=0, can_delete=True)

    def get_success_url(self):
        messages.success(self.request, f'Квитанция №{self.object.number} обновлена!')
        return reverse_lazy('receipts')

    def get_form(self, form_class=None):
        if form_class is None:
            personal_account = PersonalAccount.objects.filter(
                apartment=self.object.apartment_id).first()
            return ReceiptForm(self.request.POST or None,
                               instance=self.object,
                               initial={
                                   'house': self.object.apartment.house_id,
                                   'section': self.object.apartment.section_id,
                                   'personal_accounts': personal_account.id if personal_account else None
                               })

    def get_context_data(self, **kwargs):
        context = super(ReceiptUpdateView, self).get_context_data()
        context['formset_for_services'] = self.formset_for_services(
            self.request.POST or None,
            queryset=CalculateReceiptService.objects.filter(receipt=self.object),
            prefix='services'
        )
        context['meter_data'] = MeterData.objects.filter(apartment=self.object.apartment).select_related(
            'apartment', 'apartment__house', 'apartment__section', 'counter', 'counter__u_measurement'
        ).order_by('-id')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset_for_services = context['formset_for_services']
        personal_account = get_object_or_404(PersonalAccount, id=form.cleaned_data['personal_accounts'])
        self.object = form.save(commit=False)
        self.object.personal_account = personal_account
        self.object.save()
        sum = 0
        if formset_for_services.is_valid():
            for forms in formset_for_services:
                if forms.cleaned_data and forms.cleaned_data['DELETE'] is False:
                    if forms.is_valid():
                        services = forms.save(commit=False)
                        services.receipt = self.object
                        services.save()
            formset_for_services.save()
            sum_save = form.save(commit=False)
            sum_save.sum = sum
            sum_save.save()
            return super().form_valid(form)
        messages.error(self.request, formset_for_services.errors)
        return self.form_invalid(form)


class ReceiptDelete(DeleteView):
    model = Receipt

    def get_success_url(self):
        messages.success(self.request, f'Квитанция №{self.object.number} удалена!')
        return reverse_lazy('receipts')


# endregion Receipts


# region Receipt Template

class ReceiptTemplateListView(ListView):
    model = ReceiptTemplate
    template_name = 'crm/pages/receipts/list_templates.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return self.model.objects.order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receipt'] = Receipt.objects.filter(id=self.kwargs.get('pk')).first()
        return context


def receipt_template(request, pk):
    if request.method == 'POST':
        receipt = Receipt.objects.filter(id=pk).first()
        if 'action_send_email' in request.POST:
            if receipt.apartment.owner:
                id = request.POST.get('template')
                send_receipt_for_owner.delay(pk, id)
                messages.success(request, f'Квитанция №{receipt.number} отправлена владельцу')
            else:
                messages.error(request, f'Квитанция №{receipt.number} не имеет конечного получателя')
        else:
            file = get_object_or_404(ReceiptTemplate, id=request.POST.get('template'))
            requisites = Requisites.objects.all().first()
            services = CalculateReceiptService.objects.filter(receipt=receipt.id).select_related(
                'services', 'receipt'
            )
            account_balance = PersonalAccount.objects.filter(
                id=receipt.personal_account_id, cash_account__status=True, apartment__receipt_apartment__status=True
            ).annotate(
                balance=
                Greatest(Sum('cash_account__sum'), Decimal(0))
                -
                Greatest(Sum('apartment__receipt_apartment__calculate_receipt__cost', distinct='id'), Decimal(0))
            ).first()

            write = write_to_file(
                receipt, receipt.personal_account, requisites.description, file, services, account_balance
            )

            response = HttpResponse(save_virtual_workbook(write), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=tpl-' + str(file.id) + '.xlsx'
            return response
    return HttpResponseRedirect('/admin/receipt/templates/' + str(pk) + '/')


class SettingsTemplate(CreateView):
    model = ReceiptTemplate
    template_name = 'crm/pages/receipts/settings_templates.html'

    def get_success_url(self):
        messages.success(self.request, f'Добавлен новый шаблон')
        return reverse_lazy('settings_templates', kwargs={'pk': self.kwargs.get('pk')})

    def get_form(self, form_class=None):
        if form_class is None:
            return SettingsTemplatesForm(self.request.POST or None,
                                         self.request.FILES or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receipt_id'] = self.kwargs.get('pk')
        context['templates'] = ReceiptTemplate.objects.all().order_by('id')
        return context


class ReceiptTemplateDelete(DeleteView):
    model = ReceiptTemplate

    def get_success_url(self):
        messages.success(self.request, f'{self.object.name} удалён!')
        return reverse_lazy('settings_templates', kwargs={'pk': self.kwargs.get('slug')})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_default is True:
            messages.error(request, 'Нельзя удалить шаблон по-умолчанию')
            return HttpResponseRedirect(reverse_lazy('settings_templates', kwargs={'pk': self.kwargs.get('slug')}))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


def receipt_templates_edit(request, pk, slug):
    templates = ReceiptTemplate.objects.all()
    if request.method == 'POST':
        templates.update(is_default=False)
        templates.filter(id=pk).update(is_default=True)
        messages.success(request, 'Назначен новый шаблон по-умолчанию')
    return HttpResponseRedirect(reverse_lazy('settings_templates', kwargs={'pk': slug}))


def receipt_templates_upload(request, pk):
    file = get_object_or_404(ReceiptTemplate, id=pk)
    response = HttpResponse(file.template, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=tpl-' + str(file.id) + '.xlsx'
    return response


# endregion Receipt Template


# region Accounts

class AccountsListView(ListView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/list_accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        queryset = self.model.objects.select_related(
            'apartment', 'apartment__house', 'apartment__section', 'apartment__owner'
        ).annotate(
            balance=
            Greatest(Sum('cash_account__sum', filter=Q(cash_account__status=True), distinct=True), Decimal(0))
            -
            Greatest(Sum('receipt_account__sum', filter=Q(receipt_account__status=True), distinct=True), Decimal(0))
        ).order_by('-id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cash_balance'] = get_balance_cash()
        context['account_balance'] = get_balance_account()[1]
        context['account_debit'] = get_balance_account()[0]
        return context


class AccountsDetailView(DetailView):
    model = PersonalAccount
    template_name = 'crm/pages/accounts/detail_accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return self.model.objects.select_related(
            'apartment', 'apartment__house', 'apartment__section', 'apartment__owner'
        ).prefetch_related(
            'cash_account', 'receipt_account'
        ).annotate(
            balance=
            Greatest(Sum('cash_account__sum', filter=Q(cash_account__status=True), distinct=True), Decimal(0))
            -
            Greatest(Sum('receipt_account__sum', filter=Q(receipt_account__status=True), distinct=True), Decimal(0))
        )

    def get_context_data(self, **kwargs):
        context = super(AccountsDetailView, self).get_context_data()
        receipt = [obj.id for obj in Receipt.objects.filter(personal_account=self.object)]
        context['income'] = CashBox.objects.filter(personal_account=self.object).aggregate(sum=Sum('sum'))
        context['expense'] = CalculateReceiptService.objects.filter(receipt__in=receipt).aggregate(sum=Sum('cost'))
        balance = 0
        income = context['income']['sum']
        expense = context['expense']['sum']
        if income is not None:
            balance += income
        if expense is not None:
            balance -= expense
        context['balance'] = balance
        return context


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

# region Messages

class MessageListView(ListView):
    model = Message
    template_name = 'crm/pages/messages/list_message.html'
    context_object_name = 'message'

    def get_queryset(self):
        return self.model.objects.select_related(
            'house', 'section', 'floor', 'apartment', 'apartment__owner'
        ).order_by('-datetime')


class MessageDetailView(DetailView):
    model = Message
    template_name = 'crm/pages/messages/detail_message.html'
    context_object_name = 'message'

    def get_queryset(self):
        return self.model.objects.select_related(
            'house', 'section', 'floor', 'apartment', 'apartment__owner'
        )


class MessageCreateAndSend(CreateView):
    model = Message
    template_name = 'crm/pages/messages/send_message.html'

    def get_success_url(self):
        messages.success(self.request, f'Сообщение отправлено!')
        return reverse_lazy('list_message')

    def get_form(self, form_class=None):
        is_debt = self.request.GET.get('debt') or None
        if form_class is None:
            if is_debt:
                return MessageForm(self.request.POST or None,
                                   initial={'is_dept': True,
                                            'topics': 'Владельцам с задолженностями',
                                            'text': '<h3>Администрация CRM24</h3>'
                                                    '<p>Просим Вас погасить задолженность</p>'})
            return MessageForm(self.request.POST or None)

    def form_valid(self, form):
        message = form.save(commit=False)
        message.sender = self.request.user
        message.save()
        return super().form_valid(form)


class MessageDelete(DeleteView):
    model = Message

    def get_success_url(self):
        messages.success(self.request, f'Сообщение  удаленно!')
        return reverse_lazy('list_message')


# endregion Messages


# region Owners


class OwnerListView(ListView):
    model = User
    template_name = 'crm/pages/owners/list_owners.html'
    context_object_name = 'owners'

    def get_queryset(self):
        return self.model.objects.filter(
            is_staff=False
        ).annotate(
            balance=
            Greatest(Sum('apartment_owner__account_apartment__cash_account__sum',
                         filter=Q(apartment_owner__account_apartment__cash_account__status=True),
                         distinct=True), Decimal(0))
            -
            Greatest(Sum('apartment_owner__account_apartment__receipt_account__sum',
                         filter=Q(apartment_owner__account_apartment__receipt_account__status=True),
                         distinct=True), Decimal(0))
        ).order_by('-id')

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
        context['apartments'] = Apartment.objects.filter(owner=self.object).select_related(
            'section', 'house', 'floor', 'tariff', 'house', 'owner')
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
        return self.model.objects.select_related(
            'section', 'floor', 'house', 'owner', 'tariff'
        ).annotate(
            balance=
            Greatest(Sum('account_apartment__cash_account__sum',
                         filter=Q(account_apartment__cash_account__status=True), distinct=True), Decimal(0))
            -
            Greatest(Sum('account_apartment__receipt_account__sum',
                         filter=Q(account_apartment__receipt_account__status=True), distinct=True), Decimal(0))
        ).order_by('-id')


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
            if personal_account.cleaned_data['number_account'] != '':
                try:
                    obj = account.get(number=personal_account.cleaned_data['number_account'])
                    if obj.apartment:
                        messages.error(self.request, 'К этому лицевому счету уже закреплена квартира')
                        return super().form_invalid(form)
                    self.object = form.save()
                    account.filter(number=personal_account.cleaned_data['number_account']).update(
                        apartment=self.object
                    )
                except PersonalAccount.DoesNotExist:
                    self.object = form.save()
                    account.create(
                        number=personal_account.cleaned_data['number_account'],
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
        obj = PersonalAccount.objects.filter(apartment=self.object).first()
        context['personal_account'] = PersonalAccountForm(
            self.request.POST or None,
            initial={'number_account': obj.number if obj else None},
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
            if personal_account.cleaned_data['number_account'] != '':
                try:
                    obj = account.get(number=personal_account.cleaned_data['number_account'])
                    if obj.apartment and obj.apartment != self.object:
                        messages.error(self.request, 'К этому лицевому счету уже закреплена квартира')
                        return super().form_invalid(form)
                    account.filter(apartment=self.object).update(apartment=None)
                    account.filter(
                        number=personal_account.cleaned_data['number_account']
                    ).update(apartment=self.object)

                except PersonalAccount.DoesNotExist:
                    account.filter(apartment=self.object).update(apartment=None)
                    account.create(
                        number=personal_account.cleaned_data['number_account'],
                        apartment=self.object
                    )
        else:
            print(personal_account.errors)
            return super().form_invalid(messages.error(self.request, personal_account.errors))
        return super().form_valid(form)


class ApartmentDelete(DeleteView):
    model = Apartment

    def get_success_url(self):
        messages.success(self.request, f'Квартира №{self.object.number} удалена!')
        return reverse_lazy('apartments')


# endregion Apartment


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
                        try:
                            services_price.full_clean()
                        except ValidationError:
                            messages.error(self.request, 'У Тарифа не должно быть одинаковых Услуг')
                            self.model.objects.get(id=self.object.id).delete()
                            return self.form_invalid(formset)
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
                        try:
                            services_price.full_clean()
                        except ValidationError:
                            messages.error(self.request, 'У Тарифа не должно быть одинаковых Услуги')
                            return self.form_invalid(formset)
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
        return self.model.objects.filter(is_staff=True).order_by('role', 'id').select_related('role')


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
    form_class = UserAdminChangeForm
    template_name = 'crm/pages/users/update_user.html'

    def get_queryset(self):
        return self.model.objects.select_related('role')

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

# region Payment Items

class PaymentItemsListView(ListView):
    model = PaymentItems
    template_name = 'crm/pages/payments/list_payment_items.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return self.model.objects.all().order_by('-id')


class PaymentItemsDetailView(DetailView):
    model = PaymentItems
    template_name = 'crm/pages/payments/detail_payment_items.html'
    context_object_name = 'payment'


class PaymentItemsCreateView(CreateView):
    model = PaymentItems
    form_class = PaymentItemsForm
    template_name = 'crm/pages/payments/create_payment_items.html'

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} создан!')
        return reverse_lazy('detail_payment_items', kwargs={'pk': self.object.id})


class PaymentItemsUpdateView(UpdateView):
    model = PaymentItems
    form_class = PaymentItemsForm
    template_name = 'crm/pages/payments/update_payment_items.html'

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} обновлён!')
        return reverse_lazy('detail_payment_items', kwargs={'pk': self.object.id})


class PaymentItemsDelete(DeleteView):
    model = PaymentItems

    def get_success_url(self):
        messages.success(self.request, f'{self.object.title} удалена!')
        return reverse_lazy('payment_items')


# endregion Payment Items


# region Master's call

class MasterCallListView(ListView):
    model = CallRequest
    template_name = 'crm/pages/master_calls/list_master_calls.html'
    context_object_name = 'calls'

    def get_queryset(self):
        return self.model.objects.select_related(
            'apartment', 'master', 'type_master', 'apartment__house', 'apartment__owner'
        ).order_by('-id')


class MasterCallDetailView(DetailView):
    model = CallRequest
    template_name = 'crm/pages/master_calls/detail_master_call.html'
    context_object_name = 'call'

    def get_queryset(self):
        return self.model.objects.select_related(
            'apartment', 'master', 'type_master', 'apartment__house', 'apartment__owner'
        ).order_by('-id')


class MasterCallCreateView(CreateView):
    model = CallRequest
    form_class = MasterCallForm
    template_name = 'crm/pages/master_calls/create_master_call.html'

    def get_success_url(self):
        messages.success(self.request, f'Заявка №{self.object.id} добавлена!')
        return reverse_lazy('detail_master_call', kwargs={'pk': self.object.id})


class MasterCallUpdateView(UpdateView):
    model = CallRequest
    template_name = 'crm/pages/master_calls/update_master_call.html'

    def get_object(self, queryset=None):
        queryset = self.model.objects.filter(id=self.kwargs.get('pk')).select_related(
            'apartment', 'apartment__house', 'apartment__owner', 'apartment__section'
        )
        obj = queryset[0]
        return obj

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            return MasterCallForm(self.request.POST or None,
                                  instance=self.object,
                                  initial={'owner': self.object.apartment.owner_id,
                                           'apartment': self.object.apartment_id
                                           })

    def get_success_url(self):
        messages.success(self.request, f'Заявка №{self.object.id} обновлена!')
        return reverse_lazy('detail_master_call', kwargs={'pk': self.object.id})


class MasterCallDelete(DeleteView):
    model = CallRequest

    def get_success_url(self):
        messages.success(self.request, f'Заявка №{self.object.id} удалена!')
        return reverse_lazy('master_calls')


# endregion Master's call


# region MeterData


class MeterDataListView(ListView):
    model = MeterData
    template_name = 'crm/pages/meter_data/list_meter_data.html'
    context_object_name = 'meters_data'

    def get_queryset(self):
        queryset = self.model.objects.select_related(
            'apartment', 'counter', 'apartment__house', 'apartment__section', 'counter__u_measurement'
        ).order_by('counter', 'apartment', '-id').distinct('counter', 'apartment')
        return queryset


class MeterDataDetailView(DetailView):
    model = MeterData
    template_name = 'crm/pages/meter_data/detail_meter_data.html'
    context_object_name = 'meter_data'

    def get_queryset(self):
        return self.model.objects.select_related(
            'apartment', 'counter', 'apartment__house', 'apartment__section', 'counter__u_measurement',
            'apartment__owner'
        )


class MeterDataApartmentListView(ListView):
    model = MeterData
    template_name = 'crm/pages/meter_data/list_meter_data_for_apartment.html'
    context_object_name = 'meters_data'

    def get_queryset(self, **kwargs):
        return self.model.objects.filter(apartment=self.kwargs.get('pk')).select_related(
            'apartment', 'counter', 'apartment__house', 'apartment__section', 'counter__u_measurement'
        ).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['apartment'] = Apartment.objects.filter(id=self.kwargs.get('pk')).first()
        return context


class MeterDataCreateView(CreateView):
    model = MeterData
    template_name = 'crm/pages/meter_data/create_meter_data.html'

    def get_success_url(self):
        messages.success(self.request, f'Показания счетчика №{self.object.number} добавлены!')
        if 'action_save' in self.request.POST:
            return reverse_lazy('meter_data')
        return reverse_lazy('create_meter_data')

    def generate_number(self):
        """
        Returns the number for the initial form data
        """
        counter = 1
        while True:
            obj_id = self.model.objects.order_by('-id').first().id
            number = f'{obj_id + counter:08}'
            if not self.model.objects.filter(number=number).exists():
                return number
            counter += 1

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            apartment_id = self.request.GET.get('apartment_id', None)
            service_id = self.request.GET.get('service_id', None)
            counter = self.request.GET.get('counter', None)
            if apartment_id:
                obj = Apartment.objects.filter(pk=apartment_id).select_related(
                    'section', 'floor', 'owner', 'house'
                )[0]
                return MeterDataForm(self.request.POST or None,
                                     initial={'number': self.generate_number(),
                                              'apartment': obj,
                                              'section': obj.section_id,
                                              'house': obj.house_id,
                                              'counter': service_id or Services.objects.filter(title=counter)[0]})
            return MeterDataForm(self.request.POST or None,
                                 initial={'number': self.generate_number()})


class MeterDataUpdateView(UpdateView):
    model = MeterData
    template_name = 'crm/pages/meter_data/update_meter_data.html'

    def get_object(self, queryset=None):
        queryset = self.model.objects.filter(id=self.kwargs.get('pk')).select_related(
            'apartment', 'counter', 'counter__u_measurement'
        )
        obj = queryset[0]
        return obj

    def get_form(self, form_class=None, **kwargs):
        if form_class is None:
            return MeterDataForm(self.request.POST or None,
                                 instance=self.object,
                                 initial={'house': self.object.apartment.house_id,
                                          'section': self.object.apartment.section_id})

    def get_success_url(self):
        messages.success(self.request, f'Показания счетчика №{self.object.number} обновлены!')
        if 'action_save' in self.request.POST:
            return reverse_lazy('meter_data_for_apartment', kwargs={'pk': self.object.apartment.id})
        return reverse_lazy('create_meter_data')


class MeterDataDelete(DeleteView):
    model = MeterData

    def get_success_url(self):
        messages.success(self.request, f'Показания счетчика №{self.object.number} удалены!')
        return reverse_lazy('meter_data_for_apartment', kwargs={'pk': self.object.apartment.id})

# endregion MeterData
