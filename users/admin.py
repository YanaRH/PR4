from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'email_verified', 'is_blocked', 'is_staff')
    list_filter = ('role', 'email_verified', 'is_blocked', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Роль', {'fields': ('role', 'email_verified', 'is_blocked')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'email_verified'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_superuser and not obj.email_verified:
            obj.email_verified = True
        super().save_model(request, obj, form, change)