from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User , Follow

class CustomUserAdmin(UserAdmin):

    list_display = ('username', 'email', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', )
    
    # Editable fields
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'gender', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # create fields
    add_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'gender', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    readonly_fields = ('last_login', 'date_joined')

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)



admin.site.register(User, CustomUserAdmin)
admin.site.register(Follow)