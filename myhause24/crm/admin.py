from django.contrib import admin
from .models import House, Section, Floor, Apartment, PersonalAccount, Services, UnitOfMeasure, Tariff, \
    PriceTariffServices, Requisites, PaymentItems, MeterData, CallRequest


# Register your models here.


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    pass


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass


@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    pass


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonalAccount)
class PersonalAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    pass

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    pass


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    pass


@admin.register(PriceTariffServices)
class PriceTariffServicesAdmin(admin.ModelAdmin):
    pass


@admin.register(Requisites)
class RequisitesAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentItems)
class PaymentItemsAdmin(admin.ModelAdmin):
    pass


@admin.register(MeterData)
class MeterDataAdmin(admin.ModelAdmin):
    pass


@admin.register(CallRequest)
class CallRequestAdmin(admin.ModelAdmin):
    pass
