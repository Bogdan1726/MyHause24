from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Role
User = get_user_model()


# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
    fieldsets = (
        (None, {'fields': ('profile_picture', 'email', 'username', 'role', 'password', 'date_joined')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'patronymic',
                                                'phone', 'viber', 'telegram',
                                                'user_id', 'date_of_birth', 'status', 'about_owner')}),
        ('Разрешения', {'fields': ('is_staff', 'is_active', 'is_superuser')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


