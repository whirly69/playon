from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Campi aggiuntivi', {
            'fields': ('role', 'birth_date', 'phone', 'player_role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'player_role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')