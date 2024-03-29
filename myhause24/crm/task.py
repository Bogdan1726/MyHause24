from decimal import Decimal
from django.core.mail import send_mail, EmailMessage
from django.db.models import Sum, Q
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404
from myhause24.celery import app
from openpyxl.writer.excel import save_virtual_workbook
from .models import (
    Receipt, Requisites, CalculateReceiptService, PersonalAccount, ReceiptTemplate
)
from .services.xlsx_services import write_to_file


@app.task
def send_receipt_for_owner(pk, id):
    print('task send')
    file = get_object_or_404(ReceiptTemplate, id=id)
    receipt = Receipt.objects.filter(id=pk).first()
    requisites = Requisites.objects.all().first()
    services = CalculateReceiptService.objects.filter(receipt=receipt.id).select_related(
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
                                  cash_account__type=False)),
                     Decimal(0))
    )
    account_balance = (balance_income['sum'] - balance_expense['sum'])

    write = write_to_file(
        receipt, receipt.personal_account, requisites.description, file, services, account_balance
    )

    email = EmailMessage(
        'CRM 24 Administrations',
        f'Квитанция',
        None,
        [f'{receipt.apartment.owner.email}'],
    )

    email.attach(f'Квитанция №{receipt.number}.xlsx', save_virtual_workbook(write),
                 'application/vnd.ms-excel')
    email.send()

    print('Task completed')


@app.task
def send_email(email):
    print('task send')
    text = 'Вас приглашают подключиться к системе CRM 24.\n' \
           'Скачайте приложение:\n' \
           '\n' \
           'Play Market: https://play.google.com/store/apps/details?id=com.avadamedia.program.myhouse24&hl=uk\n' \
           'App Store: https://itunes.apple.com/us/app/%D0%BC%D0%BE%D0%B9%D0%B4%D0%BE%D0%BC24/id1308075440?l=ru&ls=1&mt=8\n' \
           'Для дальнейшей информации свяжитесь с администрацией.'
    send_mail('Приглашение в CRM 24', text,
              None,
              [email],
              fail_silently=False
              )
    print('Task completed')


@app.task
def send_new_password_owner(email, password):
    print('task send')
    send_mail(
        'CRM 24 Administrations',
        f'Ваш новый пароль - {password}',
        None,
        [email],
        fail_silently=False
    )
    print('Task completed')


@app.task
def send_invite_user(email, role):
    print('task send')
    text = f'Вас приглашают подключиться к системе CRM 24 с уровнем доступа: {role}.\n' \
           f'\n' \
           f'Ваш логин:{email}\n' \
           f'Чтобы узнать пароль свяжитесь с администрацией.\n' \
           f'\n' \
           f'Ссылка для входа: http://myhouse24.avada-media.ua/admin/'
    send_mail('Приглашение в CRM 24', text,
              None,
              [email],
              fail_silently=False
              )
    print('Task completed')
