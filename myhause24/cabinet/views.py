import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import AccessMixin
from django.db.models import Sum, Avg, Q
from django.db.models.functions import Greatest
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from openpyxl.writer.excel import save_virtual_workbook
from .services.pdf_services import write_to_file
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from crm.forms import OwnerUpdateForm, MasterCallForm
from crm.models import (
    PersonalAccount, Apartment, CallRequest, Message, PriceTariffServices,
    Receipt, ReceiptTemplate, Requisites, CalculateReceiptService, Services
)

User = get_user_model()


# Create your views here.


class OwnerRequiredMixin(View, AccessMixin):
    """
    Check user is the owner of the apartment
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('cabinet_login')
        if request.user.is_staff:
            messages.error(request, f'Вы вошли в систему как {request.user.username}, '
                                    f'однако у вас недостаточно прав для просмотра личного кабинета')
            return redirect('cabinet_login')
        if not Apartment.objects.filter(owner=request.user).exists() and \
                request.resolver_match.url_name not in ['profile', 'update_profile']:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

# region Statistics


class StatisticsOfCabinetListView(OwnerRequiredMixin):

    @staticmethod
    def get(request):
        apartment_id = request.GET.get('apartment') or None
        if apartment_id is None:
            apartment = Apartment.objects.filter(owner=request.user).first()
            return redirect(reverse_lazy('cabinet') + f'?apartment={apartment.id}')
        personal_account = PersonalAccount.objects.filter(apartment=apartment_id)
        balance_income = personal_account.aggregate(
            sum=Greatest(Sum('cash_account__sum',
                             filter=Q(cash_account__status=True,
                                      cash_account__type=True)), Decimal(0))
        )
        balance_expense = personal_account.aggregate(
            sum=Greatest(Sum('cash_account__sum',
                             filter=Q(cash_account__status=True,
                                      cash_account__type=False)),Decimal(0))
        )
        apartment_balance = (balance_income['sum'] - balance_expense['sum'])
        last_month = (datetime.now() - timedelta(days=30)).month
        list_month = [month for month in range(1, 13)]

        avg_expense = personal_account.filter(
            receipt_account__date__month=datetime.now().month
        ).aggregate(
            avg=Greatest(Avg('receipt_account__sum', filter=Q(receipt_account__status=True)), Decimal(0))
        )
        expense_to_month = personal_account.filter(
            receipt_account__date__month=last_month
        ).values(
            'receipt_account__calculate_receipt__services__title'
        ).annotate(
            sum=Sum('receipt_account__calculate_receipt__cost', filter=Q(receipt_account__status=True))
        )

        expense_to_year = personal_account.filter(
            receipt_account__date__year=datetime.now().year
        ).values(
            'receipt_account__calculate_receipt__services__title'
        ).annotate(
            sum=Sum('receipt_account__calculate_receipt__cost', filter=Q(receipt_account__status=True))
        )

        monthly_expenses_per_year = personal_account.filter(
            receipt_account__status=True, receipt_account__date__year=datetime.now().year
        ).annotate(
            sum=Sum('receipt_account__sum', filter=Q(receipt_account__status=True))
        ).values('receipt_account__date__month', 'sum')

        expense_to_month_data = []
        expense_to_year_data = []
        monthly_expenses_per_year_data = []

        for expense in expense_to_month:
            expense_to_month_data.append({
                'service': expense['receipt_account__calculate_receipt__services__title'],
                'sum': str(expense['sum'])
            })

        for expense in expense_to_year:
            expense_to_year_data.append({
                'service': expense['receipt_account__calculate_receipt__services__title'],
                'sum': str(expense['sum'])
            })

        for month in list_month:
            expense_sum = 0

            for expense in monthly_expenses_per_year:
                if expense['receipt_account__date__month'] == month:
                    expense_sum += expense['sum']

            monthly_expenses_per_year_data.append({
                'month': month, 'sum': str(expense_sum)
            })

        context = {
            'personal_account': personal_account.first(),
            'avg_expense': avg_expense,
            'apartment_balance': apartment_balance,
            'expense_to_month': json.dumps(expense_to_month_data) or None,
            'expense_to_year': json.dumps(expense_to_year_data) or None,
            'monthly_expenses_per_year': json.dumps(monthly_expenses_per_year_data) or None,
        }
        return render(request, 'cabinet/pages/index.html', context)


# endregion Statistics


# region Receipts

class ReceiptOfOwnerListView(ListView, OwnerRequiredMixin):
    model = Receipt
    template_name = 'cabinet/pages/receipt/list_receipts.html'
    context_object_name = 'receipts'

    def get_queryset(self):
        apartment_id = [obj.id for obj in Apartment.objects.filter(owner=self.request.user)]
        if self.request.GET.get('apartment'):
            apartment = get_object_or_404(Apartment, id=self.request.GET.get('apartment'))
            if apartment:
                return self.model.objects.filter(apartment=apartment, status=True)
        return self.model.objects.filter(
            apartment_id__in=apartment_id, status=True
        )


class ReceiptOfOwnerDetailView(DetailView, OwnerRequiredMixin):
    model = Receipt
    template_name = 'cabinet/pages/receipt/detail_receipt.html'
    context_object_name = 'receipt'

    def get_queryset(self):
        return self.model.objects.prefetch_related(
            'calculate_receipt__services__u_measurement'
        )


def pay_by_receipt(request, pk):
    if request.method == 'POST':
        Receipt.objects.filter(id=pk).update(status_pay='paid')
        messages.success(request, 'Квитанция успешно оплачена')
    return HttpResponseRedirect(reverse_lazy('detail-receipt', kwargs={'pk': pk}))


def export_pdf(request, pk):
    file = ReceiptTemplate.objects.all().first()
    requisites = Requisites.objects.all().first()
    receipt = Receipt.objects.filter(id=pk).first()
    services = CalculateReceiptService.objects.filter(receipt_id=receipt).select_related(
        'services', 'receipt'
    )
    personal_account = PersonalAccount.objects.filter(id=receipt.personal_account_id)
    balance_income = personal_account.aggregate(
        sum=Greatest(Sum('cash_account__sum',
                         filter=Q(cash_account__status=True,
                                  cash_account__type=True)), Decimal(0))
    )
    balance_expense = personal_account.aggregate(
        sum=Greatest(Sum('cash_account__sum',
                         filter=Q(cash_account__status=True,
                                  cash_account__type=False)), Decimal(0))
    )
    account_balance = (balance_income['sum'] - balance_expense['sum'])

    write = write_to_file(
        receipt, receipt.personal_account, requisites.description, file, services, account_balance
    )

    response = HttpResponse(save_virtual_workbook(write), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=tpl-' + str(file.id) + '.xlsx'
    return response


def receipt_print(request, pk):
    receipt = Receipt.objects.get(id=pk)
    context = {
        'today': datetime.now(),
        'receipt': receipt,
        'services': CalculateReceiptService.objects.filter(receipt=receipt)
    }
    return render(request, 'cabinet/pages/receipt/receipt_print.html', context)

# endregion Receipts


# region Tariff

class ServicesOfTariffListView(ListView, OwnerRequiredMixin):
    model = PriceTariffServices
    template_name = 'cabinet/pages/services_of_tariff.html'
    context_object_name = 'services'

    def get_queryset(self):
        if self.request.GET.get('apartment'):
            apartment = get_object_or_404(Apartment, id=self.request.GET.get('apartment'))
            if apartment:
                return self.model.objects.filter(
                    tariff_id=apartment.tariff_id
                ).select_related(
                    'tariff', 'services', 'services__u_measurement'
                )
        return self.model.objects.none()


# endregion Tariff


# region Messages

class MessagesListView(ListView, OwnerRequiredMixin):
    model = Message
    template_name = 'cabinet/pages/messages/list_messages.html'


class MessageDetailView(DetailView, OwnerRequiredMixin):
    model = Message
    template_name = 'cabinet/pages/messages/detail_message.html'
    context_object_name = 'message'

    def get_queryset(self):
        return self.model.objects.select_related(
            'house', 'section', 'floor', 'apartment', 'apartment__owner', 'sender'
        )


class MessageDelete(DeleteView, OwnerRequiredMixin):
    model = Message

    def get_success_url(self):
        messages.success(self.request, "Сообщение успешно удалено!")
        return reverse_lazy('list-messages')


# endregion Messages


# region Master's call

class MasterCallListView(ListView, OwnerRequiredMixin):
    model = CallRequest
    template_name = 'cabinet/pages/master_call/list_master_call.html'
    context_object_name = 'calls'

    def get_queryset(self):
        return self.model.objects.filter(
            apartment_id__in=[obj.id for obj in Apartment.objects.filter(owner=self.request.user)]
        ).select_related(
            'apartment', 'master', 'type_master', 'apartment__house', 'apartment__owner'
        ).order_by('-id')


class MasterCallCreateView(CreateView, OwnerRequiredMixin):
    model = CallRequest
    form_class = MasterCallForm
    template_name = 'cabinet/pages/master_call/create_master_call.html'

    def get_form(self, form_class=None):
        if form_class is None:
            return MasterCallForm(self.request.POST or None,
                                  prefix='cabinet',
                                  initial={'user': self.request.user})

    def get_success_url(self):
        messages.success(self.request, f'Заявка №{self.object.id} добавлена!')
        return reverse_lazy('master-call')

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


class MasterCallDelete(DeleteView, OwnerRequiredMixin):
    model = CallRequest

    def get_success_url(self):
        messages.success(self.request, "Заявка успешно удалена!")
        return reverse_lazy('master-call')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != 'new':
            messages.error(request, 'Невозможно удалить вызов с текущим статусом')
            return HttpResponseRedirect(reverse_lazy('master-call'))
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# endregion Master's call


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
            'floor', 'section', 'house', 'tariff', 'owner', 'account_apartment'
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
