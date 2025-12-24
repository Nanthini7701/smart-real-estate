from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'username',
        'email',
        'is_owner',
        'is_tenant',
        'is_staff',
        'is_active'
    )

    list_filter = (
        'is_owner',
        'is_tenant',
        'is_staff',
        'is_active'
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Roles', {'fields': ('is_owner', 'is_tenant')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'is_owner',
                'is_tenant',
                'is_staff',
                'is_active'
            ),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)
