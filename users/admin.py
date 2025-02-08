from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    ordering = ('email',)
    list_display = ('email', 'role', 'is_staff', 'is_active')
    search_fields = ('email',)  
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Personal Info', {'fields': ('role', 'street', 'city', 'state', 'country', 'zip_code', 'phone_number', 'image')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'street', 'city', 'state', 'country', 'zip_code', 'phone_number', 'image', 'is_staff', 'is_active'),
        }),
    )