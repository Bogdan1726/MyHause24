import os

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from user.models import Role
import datetime

User = get_user_model()


# Create your models here.


# region Housing

class House(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    image1 = models.ImageField(upload_to='crm/house/', blank=True)
    image2 = models.ImageField(upload_to='crm/house/', blank=True)
    image3 = models.ImageField(upload_to='crm/house/', blank=True)
    image4 = models.ImageField(upload_to='crm/house/', blank=True)
    image5 = models.ImageField(upload_to='crm/house/', blank=True)
    user = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return f'{self.title}'


class Apartment(models.Model):
    objects = None
    number = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                              related_name='apartment_owner')
    house = models.ForeignKey('House', null=True, on_delete=models.CASCADE)
    floor = models.ForeignKey('Floor', blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey('Section', blank=True, null=True, on_delete=models.SET_NULL)
    tariff = models.ForeignKey('Tariff', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.number}'

    @property
    def select2(self):
        return f'{self.number}, {self.house.title}'


class Section(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    house = models.ForeignKey('House', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'


class Floor(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    house = models.ForeignKey('House', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}'


# endregion Housing


# region Tariffs


class Tariff(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    description = models.TextField()
    date_edit = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.title}'


class PriceTariffServices(models.Model):
    objects = None
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE)
    services = models.ForeignKey('Services', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tariff', 'services')


class Services(models.Model):
    objects = None
    title = models.CharField(max_length=64, unique=True)
    is_show_meter_data = models.BooleanField(default=False)
    u_measurement = models.ForeignKey('UnitOfMeasure', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.title}"


class UnitOfMeasure(models.Model):
    title = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.title}"


class MeterData(models.Model):
    objects = None

    class MeterStatus(models.TextChoices):
        NEW = 'new', _("Новое")
        ACCOUNTED = 'accounted', _("Учтено")
        ACCOUNTED_FOR_PAID = 'accounted_for_paid', _("Учтено и оплачено")
        ZERO = 'zero', _('Нулевое')

    number = models.CharField(max_length=8, unique=True)
    date = models.DateField(default=datetime.date.today)
    indications = models.DecimalField(max_digits=9, decimal_places=1, null=True)
    status = models.CharField(max_length=20, choices=MeterStatus.choices, default=MeterStatus.NEW)
    counter = models.ForeignKey('Services', null=True, on_delete=models.CASCADE)
    apartment = models.ForeignKey('Apartment', null=True, on_delete=models.CASCADE)


# endregion Tariffs


# region Payments


class Receipt(models.Model):
    objects = None

    class PayStatus(models.TextChoices):
        PAID = 'paid', _("Оплачена")
        PARTIALLY_PAID = 'partially_paid', _("Частично оплачена")
        NOT_PAID = 'not_paid', _("Не оплачена")

    number = models.CharField(max_length=64, unique=True)
    date = models.DateField(default=datetime.date.today)
    date_start = models.DateField(default=datetime.date.today)
    date_end = models.DateField(default=datetime.date.today)
    status = models.BooleanField(default=True)
    status_pay = models.CharField(max_length=15, choices=PayStatus.choices, default=PayStatus.NOT_PAID)
    sum = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    personal_account = models.ForeignKey('PersonalAccount', blank=True, null=True,
                                         on_delete=models.CASCADE, related_name='receipt_account')
    tariff = models.ForeignKey('Tariff', null=True, on_delete=models.CASCADE)
    apartment = models.ForeignKey('Apartment', null=True, on_delete=models.CASCADE,
                                  related_name='receipt_apartment')


class CalculateReceiptService(models.Model):
    objects = None
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    services = models.ForeignKey('Services', on_delete=models.CASCADE, null=True)
    receipt = models.ForeignKey('Receipt', on_delete=models.CASCADE, related_name='calculate_receipt')


class ReceiptTemplate(models.Model):
    objects = None

    is_default = models.BooleanField(default=False)
    name = models.CharField(max_length=64)
    template = models.FileField(upload_to='crm/receipt-templates/')

    def __str__(self):
        return os.path.basename(self.template.name)


class PersonalAccount(models.Model):
    objects = None

    class AccountStatus(models.TextChoices):
        ACTIVE = 'active', _("Активен")
        INACTIVE = 'inactive', _("Неактивен")

    number = models.CharField(max_length=11, unique=True)
    status = models.CharField(max_length=8, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)
    apartment = models.OneToOneField('Apartment', null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='account_apartment')

    def __str__(self):
        return f'{self.number}'


class CashBox(models.Model):
    objects = None
    number = models.CharField(max_length=64, unique=True)
    date = models.DateField(default=datetime.date.today)
    status = models.BooleanField(default=True)
    type = models.BooleanField(default=True)
    sum = models.DecimalField(max_digits=10, decimal_places=4)
    comment = models.TextField(blank=True)
    payment_items = models.ForeignKey('PaymentItems', blank=True, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='owner')
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='manager')
    personal_account = models.ForeignKey('PersonalAccount', blank=True, null=True,
                                         on_delete=models.SET_NULL, related_name='cash_account')
    receipt = models.ForeignKey('Receipt', blank=True, null=True, on_delete=models.SET_NULL)


class PaymentItems(models.Model):
    objects = None

    class Type(models.TextChoices):
        INCOME = "income", _("Приход")
        EXPENSE = "expense", _("Расход")

    title = models.CharField(max_length=64)
    type = models.CharField(max_length=7, choices=Type.choices, default=Type.INCOME)

    def __str__(self):
        return f'{self.title}'


class Requisites(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    description = models.TextField()


# endregion Payments


# region CallRequest and Messages

class CallRequest(models.Model):
    objects = None

    class Status(models.TextChoices):
        NEW = "new", _("Новое")
        IN_WORK = "in_work", _("В работе")
        DONE = 'done', _("Выполнено")

    date = models.DateField(default=datetime.date.today)
    time = models.TimeField()
    description = models.TextField()
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=7, choices=Status.choices,  default=Status.NEW)
    type_master = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)
    master = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)


class Message(models.Model):
    objects = None
    datetime = models.DateTimeField(auto_now_add=True)
    topics = models.CharField(max_length=64)
    text = models.TextField(blank=True)
    is_dept = models.BooleanField(default=False)
    is_all = models.BooleanField(default=False)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='owner_message')
    apartment = models.ForeignKey('Apartment', blank=True, null=True, on_delete=models.CASCADE)
    house = models.ForeignKey('House', blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey('Section', blank=True, null=True, on_delete=models.SET_NULL)
    floor = models.ForeignKey('Floor', blank=True, null=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='sender')

# endregion CallRequest and Messages
