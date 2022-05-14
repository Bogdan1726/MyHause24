from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    DoesNotExist = None

    class Status(models.TextChoices):
        ACTIVE = 'active', _("Active")
        NEW = 'new', _("New")
        DISABLED = 'disabled', _("Disabled")

    username = models.CharField(_("username"), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    patronymic = models.CharField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profile/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = PhoneNumberField(null=True, blank=True)
    viber = PhoneNumberField(null=True, blank=True)
    telegram = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    status = models.CharField(max_length=8,
                              choices=Status.choices,
                              default=Status.NEW)
    user_id = models.CharField(max_length=32, blank=True)
    about_owner = models.TextField(blank=True)
    role = models.ForeignKey('Role', null=True, blank=True, on_delete=models.SET_NULL)

    def get_full_name(self):
        """
          Return the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name}, {self.last_name}, {self.patronymic}'
        return full_name


class Role(models.Model):
    name = models.CharField(max_length=24, unique=True)
    statistics = models.BooleanField(default=False)
    cash_box = models.BooleanField(default=False)
    receipts = models.BooleanField(default=False)
    personal_accounts = models.BooleanField(default=False)
    apartments = models.BooleanField(default=False)
    owners = models.BooleanField(default=False)
    houses = models.BooleanField(default=False)
    messages = models.BooleanField(default=False)
    call_requests = models.BooleanField(default=False)
    counters = models.BooleanField(default=False)
    site_management = models.BooleanField(default=False)
    services = models.BooleanField(default=False)
    tariffs = models.BooleanField(default=False)
    roles = models.BooleanField(default=False)
    users = models.BooleanField(default=False)
    requisites = models.BooleanField(default=False)

    def __str__(self):
        return self.name
