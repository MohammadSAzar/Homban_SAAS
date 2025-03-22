from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUserModel
from .forms import AdminCustomUserCreationForm, AdminCustomUserChangeForm


class CustomUserAdmin(BaseUserAdmin):
    form = AdminCustomUserChangeForm
    add_form = AdminCustomUserCreationForm

    list_display = ('username', 'title',)
    list_filter = ('title',)
    fieldsets = (
        (None, {'fields': ('username', 'password',)}),
        ('Permissions', {'fields': ('title',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


admin.site.register(CustomUserModel, CustomUserAdmin)

