from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models
from .forms import AdminCustomUserCreationForm, AdminCustomUserChangeForm


# --------------------------------- CUM -----------------------------------
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


admin.site.register(models.CustomUserModel, CustomUserAdmin)


# --------------------------------- LOCs -----------------------------------
@admin.register(models.Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')


@admin.register(models.SubDistrict)
class SubDistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'description')


# --------------------------------- FILE ----------------------------------
@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number')


@admin.register(models.SaleFile)
class SaleFileAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'code', 'source', 'status', 'sub_district', 'address', 'price_announced', 'price_min', 'price_per_meter',
        'room', 'area', 'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'has_images', 'has_video', 'zip_file_admin',
        'datetime_created', 'datetime_expired')
    ordering = ('-datetime_created',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created', 'datetime_expired',)


@admin.register(models.RentFile)
class RentFileAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'code', 'source', 'status', 'sub_district', 'address', 'deposit_announced', 'deposit_min', 'rent_announced', 'rent_min',
        'convertable', 'room', 'area', 'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'has_images', 'has_video',
        'datetime_created', 'datetime_expired')
    ordering = ('-datetime_created',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created', 'datetime_expired',)


# --------------------------------- SERVs ---------------------------------
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'code', 'budget_announced', 'budget_max', 'budget_status', 'datetime_created')
    ordering = ('-datetime_created',)
    readonly_fields = ('code', 'datetime_created',)


@admin.register(models.Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'sale_file', 'rent_file', 'customer', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'visit', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)


@admin.register(models.Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'session', 'followup_code', 'date', 'price', 'deposit', 'rent',
                    'owner', 'customer', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type',)
    readonly_fields = ('code', 'datetime_created',)


# --------------------------------- MNGs ----------------------------------
@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('agent', 'type', 'status', 'title', 'code', 'datetime_created',)
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status', 'agent',)
    readonly_fields = ('code', 'datetime_created',)

