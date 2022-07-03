from crm.models import Receipt, CashBox, CalculateReceiptService, PersonalAccount
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast, Coalesce

from django.template import Library

register = Library()


def get_balance(value):
    cash_balance = CashBox.objects.select_related(
        'personal_account'
    ).annotate(
        income=Sum('sum')
    ).filter(personal_account_id=value, status=True, type=True)

    receipt_expense = Receipt.objects.prefetch_related(
        'calculate_receipt'
    ).annotate(
        expense=Sum('calculate_receipt__cost')
    ).filter(personal_account_id=value, status=True)

    balance = 0
    for obj in cash_balance:
        if obj.income:
            balance += obj.income
    for obj in receipt_expense:
        if obj.expense:
            balance -= obj.expense
    return balance


register.filter('get_balance', get_balance)


