from django.contrib import admin
from .models import House, Section, Floor
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