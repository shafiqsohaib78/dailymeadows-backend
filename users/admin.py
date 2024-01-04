from django.contrib import admin
from .models import (NewUser,GeneralUserAppInfo)
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    model = NewUser
    search_fields = ('unique_id','email','username', 'name',)
    list_filter = ('is_active', 'is_staff',)
    ordering = ('-created_at',)
    list_display = ('email','username', 'name',
                    'is_active', 'is_staff')
    fieldsets = (
        ('Info', {'fields': ('unique_id','email','username', 'name',)}),
        ('Permissions', {'fields': ('is_staff','is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff')}
         ),
    )


admin.site.register(NewUser, UserAdminConfig)
admin.site.register(GeneralUserAppInfo)
