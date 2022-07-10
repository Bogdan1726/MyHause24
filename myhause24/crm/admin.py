from django.contrib import admin
from .models import House, Section, Floor, Apartment, PersonalAccount, Services, UnitOfMeasure, Tariff, \
    PriceTariffServices, Requisites, PaymentItems, MeterData, CallRequest, CashBox, Receipt, ReceiptTemplate, \
    CalculateReceiptService, Message
from main.models import HomePage, ContentBlock, SeoBlock

# Register your models here.
from main.models import Gallery, Document, AboutUs


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


@admin.register(CashBox)
class CashBoxAdmin(admin.ModelAdmin):
    pass


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    pass


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(CalculateReceiptService)
class CalculateReceiptServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    pass


@admin.register(SeoBlock)
class SeoBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    pass


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    pass


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    pass



