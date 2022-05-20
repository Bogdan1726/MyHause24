from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from user.models import Role

User = get_user_model()

# Create your models here.


# region Housing

class House(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    image1 = models.ImageField(upload_to='crm/house/', blank=True)
    image2 = models.ImageField(upload_to='crm/house/', blank=True)
    image3 = models.ImageField(upload_to='crm/house/', blank=True)
    image4 = models.ImageField(upload_to='crm/house/', blank=True)
    image5 = models.ImageField(upload_to='crm/house/', blank=True)
    user = models.ManyToManyField(User, blank=True)


class Apartment(models.Model):
    number = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=7, decimal_places=2)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    house = models.ForeignKey('House', null=True, on_delete=models.CASCADE)
    floor = models.ForeignKey('Floor', blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey('Section', blank=True, null=True, on_delete=models.SET_NULL)
    tariff = models.ForeignKey('Tariff', blank=True, null=True, on_delete=models.SET_NULL)
    personal_account = models.ForeignKey('PersonalAccount', blank=True, null=True, on_delete=models.SET_NULL)


class Section(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    house = models.ForeignKey('House', on_delete=models.CASCADE)


class Floor(models.Model):
    objects = None
    title = models.CharField(max_length=64)
    house = models.ForeignKey('House', on_delete=models.CASCADE)


# endregion Housing


# region Tariffs


class Tariff(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    date_edit = models.DateTimeField(auto_now=True)


class PriceTariffServices(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE)
    services = models.ForeignKey('Services', on_delete=models.CASCADE)


class Services(models.Model):
    title = models.CharField(max_length=64)
    is_show_meter_data = models.BooleanField(default=False)
    u_measurement = models.ForeignKey('UnitOfMeasure', blank=True, null=True, on_delete=models.SET_NULL)


class UnitOfMeasure(models.Model):
    title = models.CharField(max_length=12)


class MeterData(models.Model):
    class MeterStatus(models.TextChoices):
        NEW = 'new', _("New")
        ACCOUNTED = 'accounted', _("Accounted")
        ACCOUNTED_FOR_PAID = 'accounted_for_paid', _("Accounted for and paid")
        ZERO = 'zero', _('Zero')

    number = models.CharField(max_length=64)
    date = models.DateField(auto_now_add=True)
    indications = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=MeterStatus.choices)
    counter = models.ForeignKey('Services', blank=True, null=True, on_delete=models.SET_NULL)
    apartment = models.ForeignKey('Apartment', null=True, on_delete=models.SET_NULL)


# endregion Tariffs


# region Payments


class Receipt(models.Model):
    class PayStatus(models.TextChoices):
        PAID = 'paid', _("Paid")
        PARTIALLY_PAID = 'partially_paid', _("Partially paid")
        NOT_PAID = 'not_paid', _("Not paid")

    number = models.CharField(max_length=64)
    date = models.DateField(auto_now_add=True)
    date_start = models.DateField()
    date_end = models.DateField()
    status = models.BooleanField(default=True)
    status_pay = models.CharField(max_length=15, choices=PayStatus.choices)
    tariff = models.ForeignKey('Tariff', null=True, on_delete=models.SET_NULL)
    apartment = models.ForeignKey('Apartment', null=True, on_delete=models.SET_NULL)


class CalculateReceiptService(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    services = models.ForeignKey('Services', on_delete=models.CASCADE)
    receipt = models.ForeignKey('Receipt', on_delete=models.CASCADE)


class PersonalAccount(models.Model):
    class AccountStatus(models.TextChoices):
        ACTIVE = 'active', _("Active")
        INACTIVE = 'inactive', _("Inactive")

    number = models.CharField(max_length=64)
    status = models.CharField(max_length=8, choices=AccountStatus.choices, default=AccountStatus.ACTIVE)


class CashBox(models.Model):
    number = models.CharField(max_length=64)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)
    type = models.BooleanField()
    sum = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)
    payment_items = models.ForeignKey('PaymentItems', blank=True, null=True, on_delete=models.SET_NULL)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='owner')
    manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='manager')
    personal_account = models.ForeignKey('PersonalAccount', blank=True, null=True, on_delete=models.SET_NULL)
    receipt = models.ForeignKey('Receipt', blank=True, null=True, on_delete=models.SET_NULL)


class PaymentItems(models.Model):
    class Type(models.TextChoices):
        INCOME = "income", _("Income")
        EXPENSE = "expense", _("Expense")

    title = models.CharField(max_length=64)
    type = models.CharField(max_length=7, choices=Type.choices, default=Type.INCOME)


class Requisites(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()

# endregion Payments


# region CallRequest and Messages

class CallRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("New")
        IN_WORK = "in_work", _("In work")
        DONE = 'done', _("Done")

    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    description = models.TextField()
    comment = models.TextField()
    status = models.CharField(max_length=7, choices=Status.choices)
    type_master = models.ForeignKey(Role, blank=True, null=True, on_delete=models.SET_NULL)
    master = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE)


class Message(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    topics = models.CharField(max_length=64)
    text = models.TextField()
    is_dept = models.BooleanField(default=False)
    is_all = models.BooleanField(default=False)
    apartment = models.ForeignKey('Apartment', blank=True, null=True, on_delete=models.SET_NULL)
    house = models.ForeignKey('House', blank=True, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey('Section', blank=True, null=True, on_delete=models.SET_NULL)
    floor = models.ForeignKey('Floor', blank=True, null=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)



# endregion CallRequest and Messages







