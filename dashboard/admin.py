from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.conf import settings

from . import models
from .forms import AdminCustomUserCreationForm, AdminCustomUserChangeForm, TaskAdminForm


# --------------------------------- CUM -----------------------------------
class CustomUserAdmin(BaseUserAdmin):
    form = AdminCustomUserChangeForm
    add_form = AdminCustomUserCreationForm

    list_display = ('name_family', 'username', 'title', 'sub_district', 'id',)
    list_filter = ('title',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'sub_district', 'name_family',)}),
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
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


admin.site.register(models.CustomUserModel, CustomUserAdmin)


# --------------------------------- LOC -----------------------------------
@admin.register(models.Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.SubDistrict)
class SubDistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'description', 'id')
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


# --------------------------------- FILE ----------------------------------
@admin.register(models.SaleFile)
class SaleFileAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'created_by', 'code', 'source', 'status', 'sub_district', 'street', 'price_announced', 'price_per_meter',
        'room', 'area', 'age', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.RentFile)
class RentFileAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'created_by', 'code', 'source', 'status', 'sub_district', 'street', 'deposit_announced', 'rent_announced',
        'convertable', 'room', 'area', 'age', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('status', 'sub_district',)
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


# --------------------------------- PPL ---------------------------------
@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'datetime_created')
    ordering = ('-datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'phone_number', 'code', 'budget_announced', 'datetime_created')
    ordering = ('-datetime_created',)
    readonly_fields = ('code', 'datetime_created',)
    filter_horizontal = ('sub_districts',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Renter)
class RenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'phone_number', 'code', 'deposit_announced', 'rent_announced', 'datetime_created')
    ordering = ('-datetime_created',)
    readonly_fields = ('code', 'datetime_created',)
    filter_horizontal = ('sub_districts',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


# --------------------------------- SERV ---------------------------------
@admin.register(models.Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('type', 'agent', 'code', 'sale_file', 'rent_file', 'buyer', 'renter', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('type', 'agent', 'code', 'sale_file', 'rent_file', 'buyer', 'renter', 'status', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type', 'status',)
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'session_code', 'followup_code', 'date', 'price', 'deposit', 'rent',
                    'contract_owner', 'contract_buyer', 'contract_renter', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ('type',)
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


# --------------------------------- MNGs ----------------------------------
@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('title', 'status', 'type', 'agent', 'code', 'deadline',)
    ordering = ('-datetime_created',)
    list_filter = ['type', 'status', 'deadline']
    search_fields = ['title', 'agent__username', 'code']
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.TaskBoss)
class TaskBossAdmin(admin.ModelAdmin):
    list_display = ('type', 'agent', 'code', 'condition', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ['type', 'condition']
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('agent', 'date', 'status',)
    ordering = ('-date',)
    list_filter = ['agent', 'date', 'status',]
    search_fields = ['agent']
    readonly_fields = ('date',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.ReportItem)
class ReportItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'report', 'file_code', 'customer_code', 'datetime_created',)
    ordering = ('-datetime_created',)
    list_filter = ['type',]
    readonly_fields = ('datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


@admin.register(models.Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('agent', 'type', 'code', 'sale_file', 'rent_file', 'buyer', 'renter', 'datetime_created')
    ordering = ('-datetime_created',)
    list_filter = ['type', 'agent']
    readonly_fields = ('code', 'datetime_created',)
    list_per_page = getattr(settings, 'DJANGO_ADMIN_PER_PAGE', 20)


