from django.contrib import admin
from .models import House, Section, Floor, Apartment, PersonalAccount, Services, UnitOfMeasure


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

