from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import AccessMixin
from django.db.models import Sum, Q
from django.db.models.functions import Greatest
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from crm.models import (
    PersonalAccount, Apartment, CallRequest, Message, PriceTariffServices,
    Receipt, ReceiptTemplate, Requisites, CalculateReceiptService
)
from crm.forms import OwnerUpdateForm, MasterCallForm

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

# def download_pdf_receipt(request, pk):
#     file = ReceiptTemplate.objects.all().first
#     requisites = Requisites.objects.all().first()
#     receipt = Receipt.objects.filter(id=pk).first()
#     services = CalculateReceiptService.objects.filter(receipt_id=receipt).select_related(
#         'services', 'receipt'
#     )
#     account_balance = PersonalAccount.objects.filter(
#         id=receipt.personal_account_id
#     ).annotate(
#         balance=
#         Greatest(Sum('cash_account__sum', filter=Q(cash_account__status=True), distinct=True), Decimal(0))
#         -
#         Greatest(Sum('receipt_account__sum', filter=Q(receipt_account__status=True), distinct=True), Decimal(0))
#     ).first()
#
#     # write = write_to_file(
#     #     receipt, receipt.personal_account, requisites.description, file, services, account_balance
#     # )
#
#     # response = HttpResponse(save_virtual_workbook(write), content_type='application/vnd.ms-excel')
#     # response['Content-Disposition'] = 'attachment; filename=tpl-' + str(file.id) + '.xlsx'
#     # return response
#     return HttpResponseRedirect('/cabinet/receipt/' + str(pk) + '/')



# endregion Receipts


# region Tariff


class ServicesOfTariffListView(ListView):
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
