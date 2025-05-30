from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models
from .forms import AdminCustomUserCreationForm, AdminCustomUserChangeForm, TaskAdminForm


# --------------------------------- CUM -----------------------------------
class CustomUserAdmin(BaseUserAdmin):
    form = AdminCustomUserChangeForm
    add_form = AdminCustomUserCreationForm

    list_display = ('username', 'title', 'sub_district',)
    list_filter = ('title',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'sub_district',)}),
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


# --------------------------------- LOC -----------------------------------
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
        'title', 'code', 'source', 'status', 'sub_district', 'price_announced', 'price_min', 'price_per_meter', 'room', 'area',
        'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'has_images', 'has_video', 'zip_file_admin',
        'datetime_created', 'datetime_expired')
    ordering = ('-datetime_created',)
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created', 'datetime_expired',)


@admin.register(models.RentFile)
class RentFileAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'code', 'source', 'status', 'sub_district', 'deposit_announced', 'deposit_min', 'rent_announced', 'rent_min',
        'convertable', 'room', 'area', 'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'has_images', 'has_video',
        'datetime_created', 'datetime_expired')
    ordering = ('-datetime_created',)
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created', 'datetime_expired',)


# --------------------------------- PPL ---------------------------------
@admin.register(models.Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'code', 'province', 'city', 'district', 'budget_announced', 'budget_status',
                    'datetime_created')
    ordering = ('-datetime_created',)
    readonly_fields = ('code', 'datetime_created',)
    filter_horizontal = ('sub_districts',)


@admin.register(models.Renter)
class RenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'code', 'province', 'city', 'district', 'deposit_announced',  'rent_announced',
                    'budget_status', 'convertable', 'datetime_created')
    ordering = ('-datetime_created',)
    readonly_fields = ('code', 'datetime_created',)
    filter_horizontal = ('sub_districts',)


# --------------------------------- SERV ---------------------------------
@admin.register(models.Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('type', 'agent', 'code', 'sale_file_code', 'rent_file_code', 'buyer_code', 'renter_code', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('type', 'agent', 'code', 'sale_file_code', 'rent_file_code', 'buyer_code', 'renter_code', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)


@admin.register(models.Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'session_code', 'followup_code', 'date', 'price', 'deposit', 'rent',
                    'contract_owner', 'contract_buyer', 'contract_renter', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type',)
    readonly_fields = ('code', 'datetime_created',)


# --------------------------------- MNGs ----------------------------------
@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('title', 'status', 'type', 'agent', 'code', 'deadline',)
    ordering = ('-datetime_created',)
    list_filter = ['type', 'status', 'deadline']
    search_fields = ['title', 'agent__username', 'code']
    readonly_fields = ('code', 'datetime_created',)



