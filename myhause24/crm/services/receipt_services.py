from crm.models import CashBox
from django.shortcuts import get_object_or_404


def create_or_update_expense(request, receipt, total_sum):
    if CashBox.objects.filter(receipt=receipt).exists():
        cash = CashBox.objects.filter(receipt=receipt)
        if receipt.status_pay == 'paid':
            cash.delete()
        else:
            cash.update(sum=total_sum, status=receipt.status, personal_account=receipt.personal_account)
    else:
        if receipt.status_pay != 'paid':
            CashBox.objects.create(
                number=receipt.number,
                receipt=receipt,
                type=False,
                status=receipt.status,
                sum=receipt.sum,
                manager=request.user,
                personal_account=receipt.personal_account
            )

def delete_expense(receipt):
    if CashBox.objects.filter(receipt=receipt).exists():
        obj = get_object_or_404(CashBox, receipt=receipt)
        obj.delete()
