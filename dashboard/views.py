import os
import urllib.parse

from operator import attrgetter
from collections import defaultdict
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect

from django.views import View
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_GET, require_POST

from django.db import transaction
from django.db.models import Prefetch, Count, Q, F, Avg, Max, Case, When, IntegerField, PositiveBigIntegerField, FloatField
from django.db.models.functions import Cast

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.core.cache import cache

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

import jdatetime
from jalali_date import datetime2jalali
from datetime import datetime, timedelta
from django.utils import timezone

from . import models, forms, functions, choices
from .permissions import PermissionRequiredMixin, ReadOnlyPermissionMixin


# ---------------------------------- Dashboard ----------------------------------
def home_view(request):
    return render(request, 'dashboard/home.html')


class DashboardView(ReadOnlyPermissionMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'
    permission_model = 'Location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.title == 'bs':
            sub_districts = models.SubDistrict.objects.select_related(
                'district',
                'district__city',
                'district__city__province'
            ).prefetch_related(
                Prefetch('agents',
                         queryset=models.CustomUserModel.objects.select_related('sub_district')),
                Prefetch('agents__sale_files',
                         queryset=models.SaleFile.objects.filter(status='acc').exclude(delete_request='Yes')),
                Prefetch('agents__rent_files',
                         queryset=models.RentFile.objects.filter(status='acc').exclude(delete_request='Yes')),
                Prefetch('agents__buyers',
                         queryset=models.Buyer.objects.filter(status='acc').exclude(delete_request='Yes')),
                Prefetch('agents__renters',
                         queryset=models.Renter.objects.filter(status='acc').exclude(delete_request='Yes')),
                Prefetch('sale_files',
                         queryset=models.SaleFile.objects.filter(status='acc').exclude(delete_request='Yes')),
                Prefetch('rent_files',
                         queryset=models.RentFile.objects.filter(status='acc').exclude(delete_request='Yes')),
                'buyers', 'renters'
            ).all()
            context['sub_districts'] = sub_districts
            context['count'] = sub_districts.count()

            agents = models.CustomUserModel.objects.all()
            context['agents'] = agents
        else:
            agent = self.request.user
            context['subdi'] = agent.sub_district

            sale_files = models.SaleFile.objects.select_related(
                'agent', 'sub_district', 'person'
            ).filter(
                status='acc',
                created_by=agent
            ).exclude(delete_request='Yes')

            rent_files = models.RentFile.objects.select_related(
                'agent', 'sub_district', 'person'
            ).filter(
                status='acc',
                created_by=agent
            ).exclude(delete_request='Yes')

            buyers = models.Buyer.objects.select_related(
                'agent', 'sub_district'
            ).filter(
                status='acc',
                created_by=agent
            ).exclude(delete_request='Yes')

            renters = models.Renter.objects.select_related(
                'agent', 'sub_district'
            ).filter(
                status='acc',
                created_by=agent
            ).exclude(delete_request='Yes')

            context['sale_files'] = sale_files.count()
            context['rent_files'] = rent_files.count()
            context['buyers'] = buyers.count()
            context['renters'] = renters.count()

            today = datetime.today()
            thirty_days_ago = today - timedelta(days=30)
            seven_days_ago = today - timedelta(days=7)

            thirty_days_ago_str = thirty_days_ago.strftime('%Y/%m/%d')
            seven_days_ago_str = seven_days_ago.strftime('%Y/%m/%d')

            sessions_last_30_days = models.Session.objects.select_related(
                'agent', 'sale_file', 'rent_file', 'buyer', 'renter'
            ).filter(
                agent=agent,
                date__gte=thirty_days_ago_str
            ).count()
            sessions_last_7_days = models.Session.objects.select_related(
                'agent', 'sale_file', 'rent_file', 'buyer', 'renter'
            ).filter(
                agent=agent,
                date__gte=seven_days_ago_str
            ).count()

            context['sessions_last_30_days'] = sessions_last_30_days
            context['sessions_last_7_days'] = sessions_last_7_days
        return context


class AgentDetailView(DetailView):
    model = models.CustomUserModel
    template_name = 'dashboard/teams/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        return models.CustomUserModel.objects.select_related(
            'sub_district',
            'sub_district__district',
            'sub_district__district__city',
            'sub_district__district__city__province'
        )

    def dispatch(self, request, *args, **kwargs):
        if request.user.title != 'bs':
            raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.object

        base_filter = Q(created_by=agent, status='acc') & ~Q(delete_request='Yes')

        counts_data = dict()
        counts_data['sale_files_count'] = models.SaleFile.objects.filter(base_filter).count()
        counts_data['rent_files_count'] = models.RentFile.objects.filter(base_filter).count()
        counts_data['buyers_count'] = models.Buyer.objects.filter(base_filter).count()
        counts_data['renters_count'] = models.Renter.objects.filter(base_filter).count()

        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        sessions_counts = models.Session.objects.filter(
            agent=agent
        ).aggregate(
            sessions_30_days=Count('id', filter=Q(date__gte=thirty_days_ago)),
            sessions_7_days=Count('id', filter=Q(date__gte=seven_days_ago))
        )

        context.update({
            'sale_files': counts_data['sale_files_count'],
            'rent_files': counts_data['rent_files_count'],
            'buyers': counts_data['buyers_count'],
            'renters': counts_data['renters_count'],
            'sessions_last_30_days': sessions_counts['sessions_30_days'],
            'sessions_last_7_days': sessions_counts['sessions_7_days'],
        })
        return context


# --------------------------------- Locations --------------------------------
class LocationListView(ReadOnlyPermissionMixin, TemplateView):
    template_name = 'dashboard/locations/location_list.html'
    permission_model = 'Location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provinces = models.Province.objects.prefetch_related(
            Prefetch(
                'cities',
                queryset=models.City.objects.prefetch_related(
                    Prefetch(
                        'districts',
                        queryset=models.District.objects.prefetch_related(
                            'sub_districts'
                        ).select_related('city')
                    )
                ).select_related('province')
            )
        )

        cities = []
        districts = []
        sub_districts = []
        for province in provinces:
            for city in province.cities.all():
                cities.append(city)
                for district in city.districts.all():
                    districts.append(district)
                    sub_districts.extend(district.sub_districts.all())

        context['provinces'] = provinces
        context['cities'] = cities
        context['districts'] = districts
        context['sub_districts'] = sub_districts

        return context


class ProvinceCreateView(PermissionRequiredMixin, CreateView):
    model = models.Province
    form_class = forms.ProvinceCreateForm
    template_name = 'dashboard/locations/province_create.html'
    permission_model = 'Province'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "استان جدید در سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('location_list')


class CityCreateView(PermissionRequiredMixin, CreateView):
    model = models.City
    form_class = forms.CityCreateForm
    template_name = 'dashboard/locations/city_create.html'
    permission_model = 'City'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "شهر جدید در سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('location_list')


class DistrictCreateView(PermissionRequiredMixin, CreateView):
    model = models.District
    form_class = forms.DistrictCreateForm
    template_name = 'dashboard/locations/district_create.html'
    permission_model = 'District'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "منطقه (محله) جدید در سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('location_list')


class SubDistrictCreateView(PermissionRequiredMixin, CreateView):
    model = models.SubDistrict
    form_class = forms.SubDistrictCreateForm
    template_name = 'dashboard/locations/sub_district_create.html'
    permission_model = 'SubDistrict'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "زیرمحله جدید در سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('location_list')


class ProvinceUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Province
    form_class = forms.ProvinceCreateForm
    template_name = 'dashboard/locations/province_update.html'
    context_object_name = 'province'
    permission_model = 'Province'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('location_list')


class CityUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.City
    form_class = forms.CityCreateForm
    template_name = 'dashboard/locations/city_update.html'
    context_object_name = 'city'
    permission_model = 'City'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('location_list')


class DistrictUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.District
    form_class = forms.DistrictCreateForm
    template_name = 'dashboard/locations/district_update.html'
    context_object_name = 'district'
    permission_model = 'District'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('location_list')


class SubDistrictUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.SubDistrict
    form_class = forms.SubDistrictCreateForm
    template_name = 'dashboard/locations/sub_district_update.html'
    context_object_name = 'sub_district'
    permission_model = 'SubDistrict'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('location_list')


class ProvinceDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Province
    template_name = 'dashboard/locations/province_delete.html'
    success_url = reverse_lazy('location_list')
    context_object_name = 'province'
    permission_model = 'Province'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "استان مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class CityDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.City
    template_name = 'dashboard/locations/city_delete.html'
    success_url = reverse_lazy('location_list')
    context_object_name = 'city'
    permission_model = 'City'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "شهر مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class DistrictDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.District
    template_name = 'dashboard/locations/district_delete.html'
    success_url = reverse_lazy('location_list')
    context_object_name = 'district'
    permission_model = 'District'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "محله (منطقه) مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class SubDistrictDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.SubDistrict
    template_name = 'dashboard/locations/sub_district_delete.html'
    success_url = reverse_lazy('location_list')
    context_object_name = 'sub_district'
    permission_model = 'SubDistrict'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "زیرمحله مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


# --------------------------------- Sale Files --------------------------------
class SaleFileListView(ReadOnlyPermissionMixin, ListView):
    model = models.SaleFile
    template_name = 'dashboard/files/sale_file_list.html'
    context_object_name = 'sale_files'
    paginate_by = 12
    permission_model = 'SaleFile'

    def get_queryset(self):
        if self.request.user.title != 'bs' and self.request.user.title != 'nd':  # NEW
            sub_district = self.request.user.sub_district
            queryset_default = (
                models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person', 'created_by')
                .filter(sub_district=sub_district)).filter(status='acc').exclude(delete_request='Yes')
            form = forms.SaleFileAgentFilterForm(self.request.GET)

            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['person']:
                    queryset_filtered = queryset_filtered.filter(person=form.cleaned_data['person'])
                if form.cleaned_data['source']:
                    queryset_filtered = queryset_filtered.filter(source=form.cleaned_data['source'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])
                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['has_images'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_images]
                if form.cleaned_data['has_images'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_images]
                if form.cleaned_data['has_video'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_video]
                if form.cleaned_data['has_video'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_video]
                if form.cleaned_data['min_price']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.price_announced and obj.price_announced >= form.cleaned_data[
                                             'min_price']]
                if form.cleaned_data['max_price']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.price_announced and obj.price_announced <= form.cleaned_data[
                                             'max_price']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area <= form.cleaned_data['max_area']]
                if form.cleaned_data['min_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) >= int(form.cleaned_data['min_room'])]
                if form.cleaned_data['max_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) <= int(form.cleaned_data['max_room'])]
                if form.cleaned_data['min_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) >= int(form.cleaned_data['min_age'])]
                if form.cleaned_data['max_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) <= int(form.cleaned_data['max_age'])]
                if form.cleaned_data['min_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) >= int(form.cleaned_data['min_level'])]
                if form.cleaned_data['max_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) <= int(form.cleaned_data['max_level'])]
                if form.cleaned_data['min_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['min_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_min_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() >= gregorian_min_date]
                    except (ValueError, IndexError):
                        pass
                if form.cleaned_data['max_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['max_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_max_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() <= gregorian_max_date]
                    except (ValueError, IndexError):
                        pass

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = (
                models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person', 'created_by')
                .filter(status='acc')).exclude(delete_request='Yes')
            form = forms.SaleFileFilterForm(self.request.GET)

            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_district']:
                    queryset_filtered = queryset_filtered.filter(sub_district=form.cleaned_data['sub_district'])
                if form.cleaned_data['person']:
                    queryset_filtered = queryset_filtered.filter(person=form.cleaned_data['person'])
                if form.cleaned_data['source']:
                    queryset_filtered = queryset_filtered.filter(source=form.cleaned_data['source'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])
                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['has_images'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_images]
                if form.cleaned_data['has_images'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_images]
                if form.cleaned_data['has_video'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_video]
                if form.cleaned_data['has_video'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_video]

                if form.cleaned_data['min_price']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.price_announced and obj.price_announced >= form.cleaned_data['min_price']]
                if form.cleaned_data['max_price']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.price_announced and obj.price_announced <= form.cleaned_data['max_price']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area <= form.cleaned_data['max_area']]
                if form.cleaned_data['min_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) >= int(form.cleaned_data['min_room'])]
                if form.cleaned_data['max_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) <= int(form.cleaned_data['max_room'])]
                if form.cleaned_data['min_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) >= int(form.cleaned_data['min_age'])]
                if form.cleaned_data['max_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) <= int(form.cleaned_data['max_age'])]
                if form.cleaned_data['min_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) >= int(form.cleaned_data['min_level'])]
                if form.cleaned_data['max_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) <= int(form.cleaned_data['max_level'])]
                if form.cleaned_data['min_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['min_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_min_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() >= gregorian_min_date]
                    except (ValueError, IndexError):
                        pass
                if form.cleaned_data['max_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['max_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_max_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() <= gregorian_max_date]
                    except (ValueError, IndexError):
                        pass

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.title == 'fp' or self.request.user.title == 'nd':  # NEW
            form = forms.SaleFileAgentFilterForm(self.request.GET)
        else:
            form = forms.SaleFileFilterForm(self.request.GET)
            if self.request.GET.get('province'):
                form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
            if self.request.GET.get('city'):
                form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
            if self.request.GET.get('district'):
                form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(
                    district_id=self.request.GET.get('district'))
        context['filter_form'] = form

        # Marking
        marked_sale_file_ids = set()
        if self.request.user.is_authenticated:
            marked_sale_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    sale_file__isnull=False
                ).values_list('sale_file_id', flat=True)
            )
        context['marked_sale_file_ids'] = marked_sale_file_ids
        return context


class SaleFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    permission_model = 'SaleFile'

    def get_queryset(self):
        return models.SaleFile.objects.select_related(
            'created_by', 'created_by__sub_district', 'created_by__sub_district__district',
            'created_by__sub_district__district__city', 'created_by__sub_district__district__city__province',
            'sub_district', 'sub_district__district', 'sub_district__district__city',
            'sub_district__district__city__province', 'person'
        )

    def get_object(self, queryset=None):
        # Cache the object to avoid duplicate queries
        if not hasattr(self, '_cached_object'):
            if queryset is None:
                queryset = self.get_queryset()
            self._cached_object = super().get_object(queryset=queryset)
        return self._cached_object

    def get_template_names(self):
        if 'suggested' in self.request.path:
            return 'dashboard/files/sale_file_detail_suggested.html'
        else:
            return 'dashboard/files/sale_file_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.title != 'bs' and user.title != 'nd':  # NEW
            sale_file = self.get_object()
            if sale_file.delete_request == 'Yes':
                raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_file = self.get_object()

        suggested_buyers_queryset = models.Buyer.objects.select_related(
            'created_by', 'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts'
        ).filter(
            status='acc',
            budget_announced__gt=0.9 * sale_file.price_announced,
            budget_announced__lt=1.1 * sale_file.price_announced,
            area_min__gt=0.8 * sale_file.area,
            area_max__lt=1.2 * sale_file.area
        ).exclude(delete_request='Yes')

        paginator = Paginator(suggested_buyers_queryset, 1000)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['suggested_buyers'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        # Mark
        is_marked = False
        if self.request.user.is_authenticated:
            is_marked = models.Mark.objects.filter(
                agent=self.request.user,
                sale_file=sale_file
            ).exists()
        context['is_marked'] = is_marked

        # WA Link - Text
        context['whatsapp_share_url'] = self.get_whatsapp_share_url(sale_file)
        context['sale_file_text'] = self.get_sale_file_text(sale_file)
        return context

    def get_whatsapp_share_url(self, sale_file):
        message_parts = [
            f"🏠 فایل فروش: {sale_file.title}",
            "",
            f"قیمت: {sale_file.price_announced:,} تومان" if sale_file.price_announced else "",
            "",
            f"متراژ: {sale_file.area} متر مربع" if sale_file.area else "",
            f" تعداد اتاق: {sale_file.room}" if sale_file.room else "",
            "",
            f"  پارکینگ: {' دارد' if sale_file.parking == 'has' else ' ندارد'}",
            f" آسانسور: {' دارد' if sale_file.elevator == 'has' else ' ندارد'}",
            f"  انباری: {' دارد' if sale_file.warehouse == 'has' else ' ندارد'}",
        ]
        message = "\n".join(filter(None, message_parts))
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/?text={encoded_message}"

    def get_sale_file_text(self, sale_file):
        message_parts = [
            f"🏠 فایل فروش: {sale_file.title}",
            "",
            f"قیمت: {sale_file.price_announced:,} تومان" if sale_file.price_announced else "",
            "",
            f"متراژ: {sale_file.area} متر مربع" if sale_file.area else "",
            f" تعداد اتاق: {sale_file.room}" if sale_file.room else "",
            "",
            f"  پارکینگ: {' دارد' if sale_file.parking == 'has' else ' ندارد'}",
            f" آسانسور: {' دارد' if sale_file.elevator == 'has' else ' ندارد'}",
            f"  انباری: {' دارد' if sale_file.warehouse == 'has' else ' ندارد'}",
        ]
        return "\n".join(filter(None, message_parts))


@login_required
@require_GET
def download_sale_file_media(request, pk, unique_url_id):
    try:
        sale_file = get_object_or_404(models.SaleFile, pk=pk, unique_url_id=unique_url_id)
    except:
        try:
            sale_file = get_object_or_404(models.SaleFile, pk=pk)
        except:
            raise Http404("Sale file not found")

    # Check permissions
    user = request.user
    if hasattr(user, 'title') and user.title != 'bs' and getattr(sale_file, 'delete_request', None) == 'Yes':
        raise PermissionDenied("Access denied")

    # Get file type
    file_type = request.GET.get('file', '').strip()
    if not file_type:
        raise Http404("No file type specified")

    # Get the file field
    file_field = None
    if file_type == 'video':
        file_field = getattr(sale_file, 'video', None)
        print(f"Video field: {file_field}")
        if file_field:
            print(f"Video file name: {file_field.name}")
    elif file_type.startswith('image') and len(file_type) > 5:
        image_num = file_type[5:]
        if image_num.isdigit() and 1 <= int(image_num) <= 9:
            file_field = getattr(sale_file, f'image{image_num}', None)
            if file_field:
                print(f"Image{image_num} file name: {file_field.name}")

    if not file_field or not file_field.name:
        raise Http404("File not found")

    # Get file path and serve it
    try:
        file_path = file_field.path
        if not os.path.exists(file_path):
            raise Http404("File does not exist")
        file_size = os.path.getsize(file_path)

        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        filename = os.path.basename(file_field.name)
        extension = os.path.splitext(filename)[1].lower()

        # Set content type based on extension
        content_type_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
        }
        content_type = content_type_mapping.get(extension, 'application/octet-stream')
        print(f"Content type: {content_type}")

        # Create response
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(file_data))
        return response
    except Exception as e:
        raise Http404(f"Error serving file: {str(e)}")


class SaleFileCreateView(PermissionRequiredMixin, CreateView):
    model = models.SaleFile
    form_class = forms.SaleFileCreateForm
    template_name = 'dashboard/files/sale_file_create.html'
    permission_model = 'SaleFile'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "فایل شما در سامانه ثبت شد (این فایل توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('sale_file_list')


class SaleFileUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.SaleFile
    form_class = forms.SaleFileCreateForm
    template_name = 'dashboard/files/sale_file_update.html'
    context_object_name = 'sale_file'
    permission_model = 'SaleFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SaleFileDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.SaleFile
    template_name = 'dashboard/files/sale_file_delete.html'
    success_url = reverse_lazy('sale_file_list')
    context_object_name = 'sale_file'
    permission_model = 'SaleFile'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "فایل مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class SaleFileDeleteRequestView(PermissionRequiredMixin, UpdateView):
    model = models.SaleFile
    form_class = forms.SaleFileDeleteRequestForm
    template_name = 'dashboard/files/sale_file_delete_request.html'
    context_object_name = 'sale_file'
    permission_model = 'SaleFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('sale_file_list')


class SaleFileRecoverView(PermissionRequiredMixin, UpdateView):
    model = models.SaleFile
    form_class = forms.SaleFileRecoverForm
    template_name = 'dashboard/files/sale_file_recover.html'
    context_object_name = 'sale_file'
    permission_model = 'SaleFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('sale_file_list')


# --------------------------------- Rent Files --------------------------------
class RentFileListView(ReadOnlyPermissionMixin, ListView):
    model = models.RentFile
    template_name = 'dashboard/files/rent_file_list.html'
    context_object_name = 'rent_files'
    paginate_by = 12
    permission_model = 'RentFile'

    def get_queryset(self):
        if self.request.user.title != 'bs' and self.request.user.title != 'nd':  # NEW
            sub_district = self.request.user.sub_district
            queryset_default = (
                models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person', 'created_by')
                .filter(sub_district=sub_district)).filter(status='acc').exclude(delete_request='Yes')
            form = forms.RentFileAgentFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['person']:
                    queryset_filtered = queryset_filtered.filter(person=form.cleaned_data['person'])
                if form.cleaned_data['source']:
                    queryset_filtered = queryset_filtered.filter(source=form.cleaned_data['source'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['convertable']:
                    queryset_filtered = queryset_filtered.filter(convertable=form.cleaned_data['convertable'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])

                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['has_images'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_images]
                if form.cleaned_data['has_images'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_images]
                if form.cleaned_data['has_video'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_video]
                if form.cleaned_data['has_video'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_video]

                # queryset_final = queryset_filtered
                if form.cleaned_data['min_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data[
                                             'min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data[
                                             'max_deposit']]
                if form.cleaned_data['min_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced >= form.cleaned_data['min_rent']]
                if form.cleaned_data['max_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced <= form.cleaned_data['max_rent']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area <= form.cleaned_data['max_area']]
                if form.cleaned_data['min_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) >= int(form.cleaned_data['min_room'])]
                if form.cleaned_data['max_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) <= int(form.cleaned_data['max_room'])]
                if form.cleaned_data['min_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) >= int(form.cleaned_data['min_age'])]
                if form.cleaned_data['max_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) <= int(form.cleaned_data['max_age'])]
                if form.cleaned_data['min_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) >= int(form.cleaned_data['min_level'])]
                if form.cleaned_data['max_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) <= int(form.cleaned_data['max_level'])]
                if form.cleaned_data['min_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['min_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_min_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() >= gregorian_min_date]
                    except (ValueError, IndexError):
                        pass
                if form.cleaned_data['max_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['max_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_max_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() <= gregorian_max_date]
                    except (ValueError, IndexError):
                        pass

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = (
                models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person', 'created_by')
                .filter(status='acc')).exclude(delete_request='Yes')
            form = forms.RentFileFilterForm(self.request.GET)

            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_district']:
                    queryset_filtered = queryset_filtered.filter(sub_district=form.cleaned_data['sub_district'])
                if form.cleaned_data['person']:
                    queryset_filtered = queryset_filtered.filter(person=form.cleaned_data['person'])
                if form.cleaned_data['source']:
                    queryset_filtered = queryset_filtered.filter(source=form.cleaned_data['source'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['convertable']:
                    queryset_filtered = queryset_filtered.filter(convertable=form.cleaned_data['convertable'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])
                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['has_images'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_images]
                if form.cleaned_data['has_images'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_images]
                if form.cleaned_data['has_video'] == 'has':
                    queryset_filtered = [obj for obj in queryset_filtered if obj.has_video]
                if form.cleaned_data['has_video'] == 'hasnt':
                    queryset_filtered = [obj for obj in queryset_filtered if not obj.has_video]

                if form.cleaned_data['min_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data[
                                             'min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data[
                                             'max_deposit']]
                if form.cleaned_data['min_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced >= form.cleaned_data['min_rent']]
                if form.cleaned_data['max_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced <= form.cleaned_data['max_rent']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if obj.area <= form.cleaned_data['max_area']]
                if form.cleaned_data['min_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) >= int(form.cleaned_data['min_room'])]
                if form.cleaned_data['max_room']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.room) <= int(form.cleaned_data['max_room'])]
                if form.cleaned_data['min_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) >= int(form.cleaned_data['min_age'])]
                if form.cleaned_data['max_age']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.age) <= int(form.cleaned_data['max_age'])]
                if form.cleaned_data['min_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) >= int(form.cleaned_data['min_level'])]
                if form.cleaned_data['max_level']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         int(obj.level) <= int(form.cleaned_data['max_level'])]
                if form.cleaned_data['min_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['min_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_min_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() >= gregorian_min_date]
                    except (ValueError, IndexError):
                        pass
                if form.cleaned_data['max_date']:
                    try:
                        from datetime import datetime
                        import jdatetime
                        jalali_date_str = form.cleaned_data['max_date']
                        if '/' in jalali_date_str:
                            jalali_date_parts = jalali_date_str.split('/')
                        else:
                            jalali_date_parts = jalali_date_str.split('-')
                        jalali_date = jdatetime.date(
                            int(jalali_date_parts[0]),
                            int(jalali_date_parts[1]),
                            int(jalali_date_parts[2])
                        )
                        gregorian_max_date = jalali_date.togregorian()

                        queryset_filtered = [obj for obj in queryset_filtered if
                                             obj.datetime_created.date() <= gregorian_max_date]
                    except (ValueError, IndexError):
                        pass

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.title == 'fp' or self.request.user.title == 'nd':  # NEW
            form = forms.RentFileAgentFilterForm(self.request.GET)
        else:
            form = forms.RentFileFilterForm(self.request.GET)
            if self.request.GET.get('province'):
                form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
            if self.request.GET.get('city'):
                form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
            if self.request.GET.get('district'):
                form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(
                    district_id=self.request.GET.get('district'))
        context['filter_form'] = form

        # Marking
        marked_rent_file_ids = set()
        if self.request.user.is_authenticated:
            marked_rent_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    rent_file__isnull=False
                ).values_list('rent_file_id', flat=True)
            )
        context['marked_rent_file_ids'] = marked_rent_file_ids
        return context


class RentFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    permission_model = 'RentFile'

    def get_queryset(self):
        return models.RentFile.objects.select_related(
            'created_by', 'created_by__sub_district', 'created_by__sub_district__district',
            'created_by__sub_district__district__city', 'created_by__sub_district__district__city__province',
            'sub_district', 'sub_district__district', 'sub_district__district__city',
            'sub_district__district__city__province', 'person'
        )

    def get_object(self, queryset=None):
        if not hasattr(self, '_cached_object'):
            if queryset is None:
                queryset = self.get_queryset()
            self._cached_object = super().get_object(queryset=queryset)
        return self._cached_object

    def get_template_names(self):
        if 'suggested' in self.request.path:
            return 'dashboard/files/rent_file_detail_suggested.html'
        else:
            return 'dashboard/files/rent_file_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.title != 'bs' and user.title != 'nd':
            rent_file = self.get_object()
            if rent_file.delete_request == 'Yes':
                raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rent_file = self.get_object()

        base_queryset = models.Renter.objects.select_related(
            'created_by', 'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts'
        ).annotate(
            deposit_total_calc=Cast(F('deposit_announced') + (100 * F('rent_announced') / 3),
                                    PositiveBigIntegerField()))

        non_convertable_suggested_renters_queryset = models.Renter.objects.select_related(
            'created_by', 'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts'
        ).filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=0.8 * rent_file.deposit_announced,
            deposit_announced__lt=1.2 * rent_file.deposit_announced,
            rent_announced__gt=0.8 * rent_file.rent_announced,
            rent_announced__lt=1.2 * rent_file.rent_announced,
            area_min__gt=0.8 * rent_file.area,
            area_max__lt=1.2 * rent_file.area
        ).exclude(delete_request='Yes')

        rent_total_min = 0.8 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
        rent_total_max = 1.2 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))

        convertable_suggested_renters_queryset = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=rent_total_min,
            deposit_total_calc__lt=rent_total_max,
            area_min__gt=0.8 * rent_file.area,
            area_max__lt=1.2 * rent_file.area
        ).exclude(delete_request='Yes')

        suggested_renters_queryset = (
                non_convertable_suggested_renters_queryset | convertable_suggested_renters_queryset).distinct()

        paginator = Paginator(suggested_renters_queryset, 1000)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['suggested_renters'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        # Mark
        is_marked = False
        if self.request.user.is_authenticated:
            is_marked = models.Mark.objects.filter(
                agent=self.request.user,
                rent_file=rent_file
            ).exists()
        context['is_marked'] = is_marked

        # WA Link - Text
        context['whatsapp_share_url'] = self.get_whatsapp_share_url(rent_file)
        context['rent_file_text'] = self.get_rent_file_text(rent_file)
        return context

    def get_whatsapp_share_url(self, rent_file):
        message_parts = [
            f"🏠 فایل اجاره: {rent_file.title}",
            "",
            f"ودیعه: {rent_file.deposit_announced:,} تومان" if rent_file.deposit_announced else "",
            f"اجاره: {rent_file.rent_announced:,} تومان" if rent_file.rent_announced else "",
            "",
            f"متراژ: {rent_file.area} متر مربع" if rent_file.area else "",
            f" تعداد اتاق: {rent_file.room}" if rent_file.room else "",
            "",
            f"  پارکینگ: {' دارد' if rent_file.parking == 'has' else ' ندارد'}",
            f" آسانسور: {' دارد' if rent_file.elevator == 'has' else ' ندارد'}",
            f"  انباری: {' دارد' if rent_file.warehouse == 'has' else ' ندارد'}",
        ]
        message = "\n".join(filter(None, message_parts))
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/?text={encoded_message}"

    def get_rent_file_text(self, rent_file):
        message_parts = [
            f"🏠 فایل اجاره: {rent_file.title}",
            "",
            f"ودیعه: {rent_file.deposit_announced:,} تومان" if rent_file.deposit_announced else "",
            f"اجاره: {rent_file.rent_announced:,} تومان" if rent_file.rent_announced else "",
            "",
            f"متراژ: {rent_file.area} متر مربع" if rent_file.area else "",
            f" تعداد اتاق: {rent_file.room}" if rent_file.room else "",
            "",
            f"  پارکینگ: {' دارد' if rent_file.parking == 'has' else ' ندارد'}",
            f" آسانسور: {' دارد' if rent_file.elevator == 'has' else ' ندارد'}",
            f"  انباری: {' دارد' if rent_file.warehouse == 'has' else ' ندارد'}",
        ]
        return "\n".join(filter(None, message_parts))


@login_required
@require_GET
def download_rent_file_media(request, pk, unique_url_id):
    try:
        rent_file = get_object_or_404(models.RentFile, pk=pk, unique_url_id=unique_url_id)
    except:
        try:
            rent_file = get_object_or_404(models.RentFile, pk=pk)
        except:
            raise Http404("Rent file not found")

    # Check permissions
    user = request.user
    if hasattr(user, 'title') and user.title != 'bs' and getattr(rent_file, 'delete_request', None) == 'Yes':
        raise PermissionDenied("Access denied")

    # Get file type
    file_type = request.GET.get('file', '').strip()
    if not file_type:
        raise Http404("No file type specified")

    # Get the file field
    file_field = None
    if file_type == 'video':
        file_field = getattr(rent_file, 'video', None)
        print(f"Video field: {file_field}")
        if file_field:
            print(f"Video file name: {file_field.name}")
    elif file_type.startswith('image') and len(file_type) > 5:
        image_num = file_type[5:]
        if image_num.isdigit() and 1 <= int(image_num) <= 9:
            file_field = getattr(rent_file, f'image{image_num}', None)
            if file_field:
                print(f"Image{image_num} file name: {file_field.name}")

    if not file_field or not file_field.name:
        raise Http404("File not found")

    # Get file path and serve it
    try:
        file_path = file_field.path
        if not os.path.exists(file_path):
            raise Http404("File does not exist")
        file_size = os.path.getsize(file_path)

        # Read the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        filename = os.path.basename(file_field.name)
        extension = os.path.splitext(filename)[1].lower()

        # Set content type based on extension
        content_type_mapping = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
        }
        content_type = content_type_mapping.get(extension, 'application/octet-stream')
        print(f"Content type: {content_type}")

        # Create response
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = str(len(file_data))
        return response
    except Exception as e:
        raise Http404(f"Error serving file: {str(e)}")


class RentFileCreateView(PermissionRequiredMixin, CreateView):
    model = models.RentFile
    form_class = forms.RentFileCreateForm
    template_name = 'dashboard/files/rent_file_create.html'
    permission_model = 'RentFile'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "فایل شما در سامانه ثبت شد (این فایل توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('rent_file_list')


class RentFileUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.RentFile
    form_class = forms.RentFileCreateForm
    template_name = 'dashboard/files/rent_file_update.html'
    context_object_name = 'rent_file'
    permission_model = 'RentFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RentFileDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.RentFile
    template_name = 'dashboard/files/rent_file_delete.html'
    success_url = reverse_lazy('rent_file_list')
    context_object_name = 'rent_file'
    permission_model = 'RentFile'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "فایل مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class RentFileDeleteRequestView(PermissionRequiredMixin, UpdateView):
    model = models.RentFile
    form_class = forms.RentFileDeleteRequestForm
    template_name = 'dashboard/files/rent_file_delete_request.html'
    context_object_name = 'rent_file'
    permission_model = 'RentFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('rent_file_list')


class RentFileRecoverView(PermissionRequiredMixin, UpdateView):
    model = models.RentFile
    form_class = forms.RentFileRecoverForm
    template_name = 'dashboard/files/rent_file_recover.html'
    context_object_name = 'rent_file'
    permission_model = 'RentFile'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('rent_file_list')


# --------------------------------- Persons --------------------------------
class PersonListView(ReadOnlyPermissionMixin, ListView):
    model = models.Person
    template_name = 'dashboard/people/person_list.html'
    context_object_name = 'persons'
    paginate_by = 6
    permission_model = 'Person'

    def get_queryset(self):
        queryset = (models.Person.objects.prefetch_related('sale_files', 'rent_files')
                    .filter(status='acc').exclude(delete_request='Yes'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        duplicate_phone_numbers = (models.Person.objects
                                   .filter(status='acc')
                                   .exclude(delete_request='Yes')
                                   .values('phone_number')
                                   .annotate(count=Count('phone_number'))
                                   .filter(count__gt=1)
                                   .values_list('phone_number', flat=True))
        context['duplicate_phone_numbers'] = list(duplicate_phone_numbers)
        return context


class PersonCreateView(PermissionRequiredMixin, CreateView):
    model = models.Person
    form_class = forms.PersonCreateForm
    template_name = 'dashboard/people/person_create.html'
    permission_model = 'Person'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "فرد آگهی‌دهنده در سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('person_list')


class PersonUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PersonCreateForm
    template_name = 'dashboard/people/person_update.html'
    context_object_name = 'person'
    permission_model = 'Person'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('person_list')


class PersonDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Person
    template_name = 'dashboard/people/person_delete.html'
    success_url = reverse_lazy('person_list')
    context_object_name = 'person'
    permission_model = 'Person'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "فرد مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class PersonDeleteRequestView(PermissionRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PersonDeleteRequestForm
    template_name = 'dashboard/people/person_delete_request.html'
    context_object_name = 'person'
    permission_model = 'Person'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('person_list')


class PersonRecoverView(PermissionRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.PersonRecoverForm
    template_name = 'dashboard/people/person_recover.html'
    context_object_name = 'person'
    permission_model = 'Person'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('person_list')


# --------------------------------- Buyers --------------------------------
class BuyerListView(ReadOnlyPermissionMixin, ListView):
    model = models.Buyer
    template_name = 'dashboard/people/buyer_list.html'
    context_object_name = 'buyers'
    paginate_by = 6
    permission_model = 'Buyer'

    def get_queryset(self):
        if self.request.user.title == 'bs' or self.request.user.title == 'nd':
            queryset_default = models.Buyer.objects.select_related('province', 'city', 'district', 'created_by').prefetch_related(
                'sub_districts').exclude(delete_request='Yes').filter(status='acc')

            form = forms.BuyerFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_districts']:
                    queryset_filtered = queryset_filtered.filter(
                        sub_districts__in=form.cleaned_data['sub_districts']).distinct()
                if form.cleaned_data['budget_status']:
                    queryset_filtered = queryset_filtered.filter(budget_status=form.cleaned_data['budget_status'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])
                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['min_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced >= form.cleaned_data[
                                             'min_budget']]
                if form.cleaned_data['max_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced <= form.cleaned_data[
                                             'max_budget']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area <= form.cleaned_data['max_area']]

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = (
                (models.Buyer.objects.select_related('province', 'city', 'district', 'created_by').prefetch_related('sub_districts'))
                .exclude(delete_request='Yes').filter(status='acc').filter(created_by=self.request.user).distinct())

            form = forms.BuyerFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_districts']:
                    queryset_filtered = queryset_filtered.filter(
                        sub_districts__in=form.cleaned_data['sub_districts']).distinct()
                if form.cleaned_data['budget_status']:
                    queryset_filtered = queryset_filtered.filter(budget_status=form.cleaned_data['budget_status'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])

                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['min_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced >= form.cleaned_data[
                                             'min_budget']]
                if form.cleaned_data['max_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced <= form.cleaned_data[
                                             'max_budget']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area <= form.cleaned_data['max_area']]

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.BuyerFilterForm(self.request.GET)
        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
        duplicate_phone_numbers = (models.Buyer.objects
                                   .filter(status='acc')
                                   .exclude(delete_request='Yes')
                                   .values('phone_number')
                                   .annotate(count=Count('phone_number'))
                                   .filter(count__gt=1)
                                   .values_list('phone_number', flat=True))

        context['filter_form'] = form
        context['duplicate_phone_numbers'] = list(duplicate_phone_numbers)

        # Marking
        marked_buyer_ids = set()
        if self.request.user.is_authenticated:
            marked_buyer_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    buyer__isnull=False
                ).values_list('buyer_id', flat=True)
            )
        context['marked_buyer_ids'] = marked_buyer_ids
        return context


class BuyerDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Buyer
    context_object_name = 'buyer'
    permission_model = 'Buyer'

    def get_queryset(self):
        return models.Buyer.objects.select_related(
            'created_by', 'created_by__sub_district', 'created_by__sub_district__district',
            'created_by__sub_district__district__city', 'created_by__sub_district__district__city__province',
            'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts', 'sub_districts__district', 'sub_districts__district__city',
            'sub_districts__district__city__province'
        )

    def get_object(self, queryset=None):
        if not hasattr(self, '_cached_object'):
            if queryset is None:
                queryset = self.get_queryset()
            self._cached_object = super().get_object(queryset=queryset)
        return self._cached_object

    def get_template_names(self):
        if 'suggested' in self.request.path:
            return 'dashboard/people/buyer_detail_suggested.html'
        else:
            return 'dashboard/people/buyer_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.title != 'bs' or user.title != 'nd':
            buyer = self.get_object()
            if buyer.delete_request == 'Yes':
                raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        duplicate_phone_numbers = models.Buyer.objects.filter(
            status='acc'
        ).exclude(
            delete_request='Yes'
        ).values('phone_number').annotate(
            count=Count('phone_number')
        ).filter(
            count__gt=1
        ).values_list('phone_number', flat=True)
        context['duplicate_phone_numbers'] = list(duplicate_phone_numbers)

        buyer = self.get_object()
        price_min = 0.9 * buyer.budget_announced
        price_max = 1.1 * buyer.budget_announced
        area_min = 0.8 * buyer.area_min
        area_max = 1.2 * buyer.area_max

        suggested_files_queryset = models.SaleFile.objects.select_related(
            'created_by', 'sub_district', 'sub_district__district',
            'sub_district__district__city', 'sub_district__district__city__province',
            'person'
        ).filter(
            status='acc',
            price_announced__gt=price_min,
            price_announced__lt=price_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        # if self.request.user.title != 'bs':
        #     similar_sub_districts = buyer.sub_districts.all()
        #     suggested_files_queryset = suggested_files_queryset.filter(sub_district__in=similar_sub_districts)

        paginator = Paginator(suggested_files_queryset, 1000)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['suggested_files'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        # Mark
        is_marked = False
        if self.request.user.is_authenticated:
            is_marked = models.Mark.objects.filter(
                agent=self.request.user,
                buyer=buyer
            ).exists()
        context['is_marked'] = is_marked
        return context


class BuyerCreateView(PermissionRequiredMixin, CreateView):
    model = models.Buyer
    form_class = forms.BuyerCreateForm
    template_name = 'dashboard/people/buyer_create.html'
    permission_model = 'Buyer'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "خریدار جدید سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('buyer_list')


class BuyerUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Buyer
    form_class = forms.BuyerCreateForm
    template_name = 'dashboard/people/buyer_update.html'
    context_object_name = 'buyer'
    permission_model = 'Buyer'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('buyer_list')


class BuyerDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Buyer
    template_name = 'dashboard/people/buyer_delete.html'
    success_url = reverse_lazy('buyer_list')
    context_object_name = 'buyer'
    permission_model = 'Buyer'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "خریدار مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class BuyerDeleteRequestView(PermissionRequiredMixin, UpdateView):
    model = models.Buyer
    form_class = forms.BuyerDeleteRequestForm
    template_name = 'dashboard/people/buyer_delete_request.html'
    context_object_name = 'buyer'
    permission_model = 'Buyer'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('buyer_list')


class BuyerRecoverView(PermissionRequiredMixin, UpdateView):
    model = models.Buyer
    form_class = forms.BuyerRecoverForm
    template_name = 'dashboard/people/buyer_recover.html'
    context_object_name = 'buyer'
    permission_model = 'Buyer'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('buyer_list')


# --------------------------------- Renters --------------------------------
class RenterListView(ReadOnlyPermissionMixin, ListView):
    model = models.Renter
    template_name = 'dashboard/people/renter_list.html'
    context_object_name = 'renters'
    paginate_by = 6
    permission_model = 'Renter'

    def get_queryset(self):
        if self.request.user.title == 'bs' or self.request.user.title == 'nd':
            queryset_default = models.Renter.objects.select_related('province', 'city', 'district', 'created_by').prefetch_related(
                'sub_districts').exclude(delete_request='Yes').filter(status='acc')

            form = forms.RenterFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_districts']:
                    queryset_filtered = queryset_filtered.filter(
                        sub_districts__in=form.cleaned_data['sub_districts']).distinct()
                if form.cleaned_data['budget_status']:
                    queryset_filtered = queryset_filtered.filter(budget_status=form.cleaned_data['budget_status'])
                if form.cleaned_data['convertable']:
                    queryset_filtered = queryset_filtered.filter(convertable=form.cleaned_data['convertable'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])

                queryset_filtered = list(queryset_filtered)

                if form.cleaned_data['min_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data[
                                             'min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data[
                                             'max_deposit']]
                if form.cleaned_data['min_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced >= form.cleaned_data['min_rent']]
                if form.cleaned_data['max_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced <= form.cleaned_data['max_rent']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area <= form.cleaned_data['max_area']]

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = (
                (models.Renter.objects.select_related('province', 'city', 'district', 'created_by').prefetch_related('sub_districts'))
                .exclude(delete_request='Yes').filter(status='acc').filter(created_by=self.request.user).distinct())
            form = forms.RenterFilterForm(self.request.GET)

            if form.is_valid():
                queryset_filtered = queryset_default
                if form.cleaned_data['province']:
                    queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
                if form.cleaned_data['city']:
                    queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
                if form.cleaned_data['district']:
                    queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
                if form.cleaned_data['sub_districts']:
                    queryset_filtered = queryset_filtered.filter(
                        sub_districts__in=form.cleaned_data['sub_districts']).distinct()
                if form.cleaned_data['budget_status']:
                    queryset_filtered = queryset_filtered.filter(budget_status=form.cleaned_data['budget_status'])
                if form.cleaned_data['convertable']:
                    queryset_filtered = queryset_filtered.filter(convertable=form.cleaned_data['convertable'])
                if form.cleaned_data['document']:
                    queryset_filtered = queryset_filtered.filter(document=form.cleaned_data['document'])
                if form.cleaned_data['parking']:
                    queryset_filtered = queryset_filtered.filter(parking=form.cleaned_data['parking'])
                if form.cleaned_data['elevator']:
                    queryset_filtered = queryset_filtered.filter(elevator=form.cleaned_data['elevator'])
                if form.cleaned_data['warehouse']:
                    queryset_filtered = queryset_filtered.filter(warehouse=form.cleaned_data['warehouse'])

                queryset_filtered = list(queryset_filtered)

                # queryset_final = queryset_filtered
                if form.cleaned_data['min_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data[
                                             'min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data[
                                             'max_deposit']]
                if form.cleaned_data['min_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced >= form.cleaned_data['min_rent']]
                if form.cleaned_data['max_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced <= form.cleaned_data['max_rent']]
                if form.cleaned_data['min_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area >= form.cleaned_data['min_area']]
                if form.cleaned_data['max_area']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.area <= form.cleaned_data['max_area']]

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.RenterFilterForm(self.request.GET)
        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
        duplicate_phone_numbers = (models.Renter.objects
                                   .filter(status='acc')
                                   .exclude(delete_request='Yes')
                                   .values('phone_number')
                                   .annotate(count=Count('phone_number'))
                                   .filter(count__gt=1)
                                   .values_list('phone_number', flat=True))

        context['filter_form'] = form
        context['duplicate_phone_numbers'] = list(duplicate_phone_numbers)

        # Marking
        marked_renter_ids = set()
        if self.request.user.is_authenticated:
            marked_renter_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    renter__isnull=False
                ).values_list('renter_id', flat=True)
            )
        context['marked_renter_ids'] = marked_renter_ids
        return context


class RenterDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Renter
    context_object_name = 'renter'
    permission_model = 'Renter'

    def get_queryset(self):
        return models.Renter.objects.select_related(
            'created_by', 'created_by__sub_district', 'created_by__sub_district__district',
            'created_by__sub_district__district__city', 'created_by__sub_district__district__city__province',
            'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts', 'sub_districts__district', 'sub_districts__district__city',
            'sub_districts__district__city__province'
        )

    def get_object(self, queryset=None):
        if not hasattr(self, '_cached_object'):
            if queryset is None:
                queryset = self.get_queryset()
            self._cached_object = super().get_object(queryset=queryset)
        return self._cached_object

    def get_template_names(self):
        if 'suggested' in self.request.path:
            return 'dashboard/people/renter_detail_suggested.html'
        else:
            return 'dashboard/people/renter_detail.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.title != 'bs' or user.title == 'nd':
            renter = self.get_object()
            if renter.delete_request == 'Yes':
                raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        duplicate_phone_numbers = models.Renter.objects.filter(
            status='acc'
        ).exclude(
            delete_request='Yes'
        ).values('phone_number').annotate(
            count=Count('phone_number')
        ).filter(
            count__gt=1
        ).values_list('phone_number', flat=True)
        context['duplicate_phone_numbers'] = list(duplicate_phone_numbers)

        renter = self.get_object()
        deposit_min = 0.8 * renter.deposit_announced
        deposit_max = 1.2 * renter.deposit_announced
        rent_min = 0.8 * renter.rent_announced
        rent_max = 1.2 * renter.rent_announced
        area_min = 0.8 * renter.area_min
        area_max = 1.2 * renter.area_max
        renter_total_min = 0.8 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))
        renter_total_max = 1.2 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))

        base_queryset = models.RentFile.objects.select_related(
            'created_by', 'sub_district', 'sub_district__district',
            'sub_district__district__city', 'sub_district__district__city__province',
            'person'
        ).annotate(
            deposit_total_calc=Cast(F('deposit_announced') + (100 * F('rent_announced') / 3),
                                    PositiveBigIntegerField()))

        non_convertable_suggested_files_queryset = models.RentFile.objects.select_related(
            'created_by', 'sub_district', 'sub_district__district',
            'sub_district__district__city', 'sub_district__district__city__province',
            'person'
        ).filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=deposit_min,
            deposit_announced__lt=deposit_max,
            rent_announced__gt=rent_min,
            rent_announced__lt=rent_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        convertable_suggested_files_queryset = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=renter_total_min,
            deposit_total_calc__lt=renter_total_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        suggested_files_queryset = (
                non_convertable_suggested_files_queryset | convertable_suggested_files_queryset).distinct()
        # if self.request.user.title != 'bs':
        #     suggested_files_queryset = suggested_files_queryset.filter(sub_district__in=renter.sub_districts.all())

        paginator = Paginator(suggested_files_queryset, 1000)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['suggested_files'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()

        # Mark
        is_marked = False
        if self.request.user.is_authenticated:
            is_marked = models.Mark.objects.filter(
                agent=self.request.user,
                renter=renter
            ).exists()
        context['is_marked'] = is_marked
        return context


class RenterCreateView(PermissionRequiredMixin, CreateView):
    model = models.Renter
    form_class = forms.RenterCreateForm
    template_name = 'dashboard/people/renter_create.html'
    permission_model = 'Renter'
    permission_action = 'create'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "موجر جدید سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('renter_list')


class RenterUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Renter
    form_class = forms.RenterCreateForm
    template_name = 'dashboard/people/renter_update.html'
    context_object_name = 'renter'
    permission_model = 'Renter'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('renter_list')


class RenterDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Renter
    template_name = 'dashboard/people/renter_delete.html'
    success_url = reverse_lazy('renter_list')
    context_object_name = 'renter'
    permission_model = 'Renter'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "مستاجر مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class RenterDeleteRequestView(PermissionRequiredMixin, UpdateView):
    model = models.Renter
    form_class = forms.RenterDeleteRequestForm
    template_name = 'dashboard/people/renter_delete_request.html'
    context_object_name = 'renter'
    permission_model = 'Renter'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('renter_list')


class RenterRecoverView(PermissionRequiredMixin, UpdateView):
    model = models.Renter
    form_class = forms.RenterRecoverForm
    template_name = 'dashboard/people/renter_recover.html'
    context_object_name = 'renter'
    permission_model = 'Renter'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('renter_list')


# --------------------------------- Search ---------------------------------
class SaleFileSearchView(ReadOnlyPermissionMixin, ListView):
    model = models.SaleFile
    template_name = 'dashboard/search/sale_file_search.html'
    context_object_name = 'sale_files'
    paginate_by = 12
    permission_model = 'SaleFile'

    def get_queryset(self):
        queryset = models.SaleFile.objects.none()

        form = forms.SaleFileFilterForm(self.request.GET or None)
        if form.is_bound and form.is_valid():
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            min_area = form.cleaned_data.get('min_area')
            max_area = form.cleaned_data.get('max_area')

            if any([min_price, max_price, min_area, max_area]):
                queryset = models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district',
                                                                  'person', 'created_by').all().exclude(
                    delete_request='Yes')
                if min_price is not None:
                    queryset = queryset.filter(price_announced__gte=min_price)
                if max_price is not None:
                    queryset = queryset.filter(price_announced__lte=max_price)
                if min_area is not None:
                    queryset = queryset.filter(area__gte=min_area)
                if max_area is not None:
                    queryset = queryset.filter(area__lte=max_area)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.SaleFileFilterForm(self.request.GET or None)

        # Marking
        marked_sale_file_ids = set()
        if self.request.user.is_authenticated:
            marked_sale_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    sale_file__isnull=False
                ).values_list('sale_file_id', flat=True)
            )
        context['marked_sale_file_ids'] = marked_sale_file_ids
        return context


class RentFileSearchView(ReadOnlyPermissionMixin, ListView):
    model = models.RentFile
    template_name = 'dashboard/search/rent_file_search.html'
    context_object_name = 'rent_files'
    paginate_by = 12
    permission_model = 'RentFile'

    def get_queryset(self):
        queryset = models.RentFile.objects.none()

        form = forms.RentFileFilterForm(self.request.GET or None)
        if form.is_bound and form.is_valid():
            min_deposit = form.cleaned_data.get('min_deposit')
            max_deposit = form.cleaned_data.get('max_deposit')
            min_rent = form.cleaned_data.get('min_rent')
            max_rent = form.cleaned_data.get('max_rent')
            min_area = form.cleaned_data.get('min_area')
            max_area = form.cleaned_data.get('max_area')

            if any([min_deposit, max_deposit, min_rent, max_rent, min_area, max_area]):
                queryset = models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district',
                                                                  'person', 'created_by').all().exclude(
                    delete_request='Yes')
                if min_deposit is not None:
                    queryset = queryset.filter(deposit_announced__gte=min_deposit)
                if max_deposit is not None:
                    queryset = queryset.filter(deposit_announced__lte=max_deposit)
                if min_rent is not None:
                    queryset = queryset.filter(rent_announced__gte=min_rent)
                if max_rent is not None:
                    queryset = queryset.filter(rent_announced__lte=max_rent)
                if min_area is not None:
                    queryset = queryset.filter(area__gte=min_area)
                if max_area is not None:
                    queryset = queryset.filter(area__lte=max_area)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.RentFileFilterForm(self.request.GET or None)

        # Marking
        marked_rent_file_ids = set()
        if self.request.user.is_authenticated:
            marked_rent_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    rent_file__isnull=False
                ).values_list('rent_file_id', flat=True)
            )
        context['marked_rent_file_ids'] = marked_rent_file_ids
        return context


class BuyerSearchView(ReadOnlyPermissionMixin, ListView):
    model = models.Buyer
    template_name = 'dashboard/search/buyer_search.html'
    context_object_name = 'buyers'
    paginate_by = 12
    permission_model = 'Buyer'

    def get_queryset(self):
        user = self.request.user
        queryset = models.Buyer.objects.none()

        form = forms.BuyerFilterForm(self.request.GET or None)
        if form.is_bound and form.is_valid():
            min_budget = form.cleaned_data.get('min_budget')
            max_budget = form.cleaned_data.get('max_budget')
            min_area = form.cleaned_data.get('min_area')
            max_area = form.cleaned_data.get('max_area')

            if any([min_budget, max_budget, min_area, max_area]):
                if user.title != 'cp':
                    queryset = (models.Buyer.objects.select_related('province', 'city', 'district', 'created_by')
                                .prefetch_related('sub_districts').all().exclude(delete_request='Yes'))
                else:
                    queryset = (models.Buyer.objects.select_related('province', 'city', 'district', 'created_by')
                                .prefetch_related('sub_districts').filter(created_by=user).all().exclude(delete_request='Yes'))
                if min_budget is not None:
                    queryset = queryset.filter(budget_announced__gte=min_budget)
                if max_budget is not None:
                    queryset = queryset.filter(budget_announced__lte=max_budget)
                if min_area is not None:
                    queryset = queryset.filter(area__gte=min_area)
                if max_area is not None:
                    queryset = queryset.filter(area__lte=max_area)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.BuyerFilterForm(self.request.GET or None)

        # Marking
        marked_buyer_ids = set()
        if self.request.user.is_authenticated:
            marked_buyer_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    buyer__isnull=False
                ).values_list('buyer_id', flat=True)
            )
        context['marked_buyer_ids'] = marked_buyer_ids
        return context


class RenterSearchView(ReadOnlyPermissionMixin, ListView):
    model = models.Renter
    template_name = 'dashboard/search/renter_search.html'
    context_object_name = 'renters'
    paginate_by = 12
    permission_model = 'Renter'

    def get_queryset(self):
        user = self.request.user
        queryset = models.Renter.objects.none()

        form = forms.RenterFilterForm(self.request.GET or None)
        if form.is_bound and form.is_valid():
            min_deposit = form.cleaned_data.get('min_deposit')
            max_deposit = form.cleaned_data.get('max_deposit')
            min_rent = form.cleaned_data.get('min_rent')
            max_rent = form.cleaned_data.get('max_rent')
            min_area = form.cleaned_data.get('min_area')
            max_area = form.cleaned_data.get('max_area')

            if any([min_deposit, max_deposit, min_rent, max_rent, min_area, max_area]):
                if user.title != 'cp':
                    queryset = (models.Renter.objects.select_related('province', 'city', 'district', 'created_by')
                                .prefetch_related('sub_districts').all().exclude(delete_request='Yes'))
                else:
                    queryset = (models.Renter.objects.select_related('province', 'city', 'district', 'created_by')
                                .prefetch_related('sub_districts').filter(created_by=user).all().exclude(
                        delete_request='Yes'))
                if min_deposit is not None:
                    queryset = queryset.filter(deposit_announced__gte=min_deposit)
                if max_deposit is not None:
                    queryset = queryset.filter(deposit_announced__lte=max_deposit)
                if min_rent is not None:
                    queryset = queryset.filter(rent_announced__gte=min_rent)
                if max_rent is not None:
                    queryset = queryset.filter(rent_announced__lte=max_rent)
                if min_area is not None:
                    queryset = queryset.filter(area__gte=min_area)
                if max_area is not None:
                    queryset = queryset.filter(area__lte=max_area)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.RenterFilterForm(self.request.GET or None)

        # Marking
        marked_renter_ids = set()
        if self.request.user.is_authenticated:
            marked_renter_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    renter__isnull=False
                ).values_list('renter_id', flat=True)
            )
        context['marked_renter_ids'] = marked_renter_ids
        return context


class CodeFinderView(ReadOnlyPermissionMixin, ListView):
    template_name = 'dashboard/search/code_finder.html'
    context_object_name = 'results'
    permission_model = 'SaleFile'
    paginate_by = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_queryset = None

    def get_queryset(self):
        if self._cached_queryset is not None:
            return self._cached_queryset

        queryset = None
        form = forms.CodeFinderForm(self.request.GET)
        if form.is_valid():
            search_type = form.cleaned_data.get('type')
            search_code = form.cleaned_data.get('code')

            if search_type and search_code:
                model_mapping = {
                    'sf': models.SaleFile,
                    'rf': models.RentFile,
                    'by': models.Buyer,
                    'rt': models.Renter,
                }

                target_model = model_mapping.get(search_type)
                if target_model:
                    try:
                        queryset = self.get_optimized_queryset(target_model, search_type).filter(code=search_code)
                        if not queryset.exists():
                            queryset = target_model.objects.none()
                    except Exception as e:
                        queryset = target_model.objects.none()
                else:
                    queryset = models.SaleFile.objects.none()
            else:
                queryset = models.SaleFile.objects.none()
        else:
            queryset = models.SaleFile.objects.none()
            if self.request.GET:
                messages.error(self.request, 'ورودی نامعتبر است.')

        self._cached_queryset = queryset or models.SaleFile.objects.none()
        return self._cached_queryset

    def get_optimized_queryset(self, target_model, search_type):
        if search_type == 'sf':
            return target_model.objects.select_related(
                'created_by', 'sub_district', 'person'
            )
        elif search_type == 'rf':
            return target_model.objects.select_related(
                'created_by', 'sub_district', 'person'
            )
        elif search_type == 'by':
            return target_model.objects.select_related(
                'created_by', 'province', 'city', 'district'
            )
        elif search_type == 'rt':
            return target_model.objects.select_related(
                'created_by', 'province', 'city', 'district'
            )
        else:
            return target_model.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = forms.CodeFinderForm(self.request.GET)
        context['search_performed'] = bool(self.request.GET.get('type') and self.request.GET.get('code'))
        context['search_type'] = self.request.GET.get('type', '')
        context['search_code'] = self.request.GET.get('code', '')

        if context['search_performed'] and context['results']:
            search_type = context['search_type']
            type_mapping = {
                'sf': 'sale_file',
                'rf': 'rent_file',
                'by': 'buyer',
                'rt': 'renter',
            }
            context['result_type'] = type_mapping.get(search_type, 'unknown')

        # Marking
        marked_sale_file_ids = set()
        if self.request.user.is_authenticated:
            marked_sale_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    sale_file__isnull=False
                ).values_list('sale_file_id', flat=True)
            )
        context['marked_sale_file_ids'] = marked_sale_file_ids

        marked_rent_file_ids = set()
        if self.request.user.is_authenticated:
            marked_rent_file_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    rent_file__isnull=False
                ).values_list('rent_file_id', flat=True)
            )
        context['marked_rent_file_ids'] = marked_rent_file_ids

        marked_buyer_ids = set()
        if self.request.user.is_authenticated:
            marked_buyer_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    buyer__isnull=False
                ).values_list('buyer_id', flat=True)
            )
        context['marked_buyer_ids'] = marked_buyer_ids

        marked_renter_ids = set()
        if self.request.user.is_authenticated:
            marked_renter_ids = set(
                models.Mark.objects.filter(
                    agent=self.request.user,
                    renter__isnull=False
                ).values_list('renter_id', flat=True)
            )
        context['marked_renter_ids'] = marked_renter_ids

        return context


# --------------------------------- Marks ---------------------------------
class SaleFileMarksListView(ReadOnlyPermissionMixin, ListView):
    model = models.Mark
    template_name = 'dashboard/marks/sale_file_mark_list.html'
    context_object_name = 'sale_file_marks'
    paginate_by = 12
    permission_model = 'Mark'

    def get_queryset(self):
        agent = self.request.user
        queryset = models.Mark.objects.select_related(
            'agent',
            'sale_file',
            'sale_file__created_by',
            'sale_file__sub_district',
            'sale_file__person'
        ).filter(agent=agent, type='sf')
        return queryset


class SaleFileMarkDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Mark
    success_url = reverse_lazy('sale_file_marks')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.agent != request.user:
            return JsonResponse({
                'success': False,
                'message': 'غیر مجاز!'
            }, status=403)

        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'حذف شد!'
            })
        return super().delete(request, *args, **kwargs)


class RentFileMarksListView(ReadOnlyPermissionMixin, ListView):
    model = models.Mark
    template_name = 'dashboard/marks/rent_file_mark_list.html'
    context_object_name = 'rent_file_marks'
    paginate_by = 12
    permission_model = 'Mark'

    def get_queryset(self):
        agent = self.request.user
        queryset = models.Mark.objects.select_related(
            'agent',
            'rent_file',
            'rent_file__created_by',
            'rent_file__sub_district',
            'rent_file__person'
        ).filter(agent=agent, type='rf')
        return queryset


class RentFileMarkDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Mark
    success_url = reverse_lazy('rent_file_marks')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.agent != request.user:
            return JsonResponse({
                'success': False,
                'message': 'غیر مجاز!'
            }, status=403)

        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'حذف شد!'
            })
        return super().delete(request, *args, **kwargs)


class BuyerMarksListView(ReadOnlyPermissionMixin, ListView):
    model = models.Mark
    template_name = 'dashboard/marks/buyer_mark_list.html'
    context_object_name = 'buyer_marks'
    paginate_by = 12
    permission_model = 'Mark'

    def get_queryset(self):
        agent = self.request.user
        queryset = models.Mark.objects.select_related(
            'agent',
            'buyer',
            'buyer__created_by',
            'buyer__province',
            'buyer__city',
            'buyer__district'
        ).prefetch_related(
            'buyer__sub_districts'
        ).filter(agent=agent, type='by')
        return queryset


class BuyerMarkDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Mark
    success_url = reverse_lazy('buyer_marks')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.agent != request.user:
            return JsonResponse({
                'success': False,
                'message': 'غیر مجاز!'
            }, status=403)

        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'حذف شد!'
            })
        return super().delete(request, *args, **kwargs)


class RenterMarksListView(ReadOnlyPermissionMixin, ListView):
    model = models.Mark
    template_name = 'dashboard/marks/renter_mark_list.html'
    context_object_name = 'renter_marks'
    paginate_by = 12
    permission_model = 'Mark'

    def get_queryset(self):
        agent = self.request.user
        queryset = models.Mark.objects.select_related(
            'agent',
            'renter',
            'renter__created_by',
            'renter__province',
            'renter__city',
            'renter__district'
        ).prefetch_related(
            'renter__sub_districts'
        ).filter(agent=agent, type='rt')
        return queryset


class RenterMarkDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Mark
    success_url = reverse_lazy('renter_marks')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.agent != request.user:
            return JsonResponse({
                'success': False,
                'message': 'غیر مجاز!'
            }, status=403)

        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'حذف شد!'
            })
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def toggle_mark_sale_file(request, object_type, object_id):
    if object_type != 'sale_file':
        return JsonResponse({
            'success': False,
            'message': 'نوع نامعتبر است'
        })

    try:
        sale_file = get_object_or_404(models.SaleFile, id=object_id)

        existing_mark = models.Mark.objects.filter(
            agent=request.user,
            sale_file=sale_file
        ).first()

        if existing_mark:
            existing_mark.delete()
            return JsonResponse({
                'success': True,
                'action': 'deleted',
                'message': 'نشان حذف شد',
                'is_marked': False
            })
        else:
            mark = models.Mark.objects.create(
                agent=request.user,
                sale_file=sale_file
            )
            return JsonResponse({
                'success': True,
                'action': 'created',
                'message': 'نشان ایجاد شد',
                'is_marked': True,
                'mark_id': mark.id
            })

    except models.SaleFile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'فایل فروش یافت نشد'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطا در پردازش درخواست'
        })


@login_required
@require_POST
def toggle_mark_rent_file(request, object_type, object_id):
    if object_type != 'rent_file':
        return JsonResponse({
            'success': False,
            'message': 'نوع نامعتبر است'
        })

    try:
        rent_file = get_object_or_404(models.RentFile, id=object_id)

        existing_mark = models.Mark.objects.filter(
            agent=request.user,
            rent_file=rent_file
        ).first()

        if existing_mark:
            existing_mark.delete()
            return JsonResponse({
                'success': True,
                'action': 'deleted',
                'message': 'نشان حذف شد',
                'is_marked': False
            })
        else:
            mark = models.Mark.objects.create(
                agent=request.user,
                rent_file=rent_file
            )
            return JsonResponse({
                'success': True,
                'action': 'created',
                'message': 'نشان ایجاد شد',
                'is_marked': True,
                'mark_id': mark.id
            })

    except models.RentFile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'فایل اجاره یافت نشد'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطا در پردازش درخواست'
        })


@login_required
@require_POST
def toggle_mark_buyer(request, object_type, object_id):
    if object_type != 'buyer':
        return JsonResponse({
            'success': False,
            'message': 'نوع نامعتبر است'
        })

    try:
        buyer = get_object_or_404(models.Buyer, id=object_id)

        existing_mark = models.Mark.objects.filter(
            agent=request.user,
            buyer=buyer
        ).first()

        if existing_mark:
            existing_mark.delete()
            return JsonResponse({
                'success': True,
                'action': 'deleted',
                'message': 'نشان حذف شد',
                'is_marked': False
            })
        else:
            mark = models.Mark.objects.create(
                agent=request.user,
                buyer=buyer
            )
            return JsonResponse({
                'success': True,
                'action': 'created',
                'message': 'نشان ایجاد شد',
                'is_marked': True,
                'mark_id': mark.id
            })

    except models.Buyer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'خریدار یافت نشد'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطا در پردازش درخواست'
        })


@login_required
@require_POST
def toggle_mark_renter(request, object_type, object_id):
    if object_type != 'renter':
        return JsonResponse({
            'success': False,
            'message': 'نوع نامعتبر است'
        })

    try:
        renter = get_object_or_404(models.Renter, id=object_id)

        existing_mark = models.Mark.objects.filter(
            agent=request.user,
            renter=renter
        ).first()

        if existing_mark:
            existing_mark.delete()
            return JsonResponse({
                'success': True,
                'action': 'deleted',
                'message': 'نشان حذف شد',
                'is_marked': False
            })
        else:
            mark = models.Mark.objects.create(
                agent=request.user,
                renter=renter
            )
            return JsonResponse({
                'success': True,
                'action': 'created',
                'message': 'نشان ایجاد شد',
                'is_marked': True,
                'mark_id': mark.id
            })

    except models.Renter.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'مستاجر یافت نشد'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'خطا در پردازش درخواست'
        })


# -------------------------------- Reminders -------------------------------
class ReminderListView(ReadOnlyPermissionMixin, ListView):
    model = models.Reminder
    template_name = 'dashboard/reminders/reminder_list.html'
    context_object_name = 'reminders'
    paginate_by = 6
    permission_model = 'Reminder'

    def get_queryset(self):
        agent = self.request.user
        queryset = models.Reminder.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                      'agent__sub_district').filter(agent=agent)
        return queryset


class ReminderCreateView(PermissionRequiredMixin, CreateView):
    model = models.Reminder
    form_class = forms.ReminderCreateForm
    template_name = 'dashboard/reminders/reminder_create.html'
    permission_model = 'Reminder'
    permission_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        date = self.request.GET.get('date')
        if date:
            initial['date'] = date
        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "یادآور جدید در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('reminder_list')


class ReminderDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Reminder
    template_name = 'dashboard/reminders/reminder_delete.html'
    success_url = reverse_lazy('reminder_list')
    context_object_name = 'reminder'
    permission_model = 'Reminder'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "یادآور مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


def dated_reminder_list_view(request):
    user = request.user
    date = request.GET.get('date')
    reminders = models.Reminder.objects.filter(agent=user)
    if date:
        if user.title != 'bs':
            reminders = (models.Reminder.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter')
                         .filter(agent=user).filter(date=date))
    context = {
        'user': user,
        'date': date,
                'reminders': reminders,
    }
    return render(request, 'dashboard/reminders/dated_reminder_list.html', context=context)


# -------------------------------- BossTasks -------------------------------
class TaskBossListView(ListView):
    model = models.TaskBoss
    template_name = 'dashboard/boss/boss_task_list.html'
    context_object_name = 'boss_tasks'
    paginate_by = 12

    def get_queryset(self):
        queryset = models.TaskBoss.objects.select_related(
            'new_sale_file',
            'new_sale_file__created_by',
            'new_sale_file__sub_district',
            'new_sale_file__person',

            'new_rent_file',
            'new_rent_file__created_by',
            'new_rent_file__sub_district',
            'new_rent_file__person',

            'new_buyer',
            'new_buyer__created_by',
            'new_buyer__province',
            'new_buyer__city',
            'new_buyer__district',

            'new_renter',
            'new_renter__created_by',
            'new_renter__province',
            'new_renter__city',
            'new_renter__district',

            'new_person',
            'new_person__created_by',

            'new_session',
            'new_session__agent',
            'new_session__sale_file',
            'new_session__rent_file',
            'new_session__buyer',
            'new_session__renter',

            'result_session',
            'result_session__agent'
        ).prefetch_related(
            'new_buyer__sub_districts',
            'new_renter__sub_districts'
        ).filter(condition='op')

        form = forms.TaskBossFilterForm(self.request.GET)
        if form.is_valid() and form.cleaned_data.get('type'):
            queryset = queryset.filter(type=form.cleaned_data['type'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = forms.TaskBossFilterForm(self.request.GET)
        return context


class TaskBossApproveView(View):
    template_name = 'dashboard/boss/boss_task_approve.html'

    def get(self, request, pk, code):
        boss_task = get_object_or_404(models.TaskBoss, pk=pk, code=code)
        if boss_task.type == 'sf':
            sale_file = boss_task.new_sale_file
            form = forms.CombinedSaleFileStatusForm(sale_file_instance=sale_file, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'sale_file': sale_file,
            })
        if boss_task.type == 'rf':
            rent_file = boss_task.new_rent_file
            form = forms.CombinedRentFileStatusForm(rent_file_instance=rent_file, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'rent_file': rent_file,
            })
        if boss_task.type == 'by':
            buyer = boss_task.new_buyer
            form = forms.CombinedBuyerStatusForm(buyer_instance=buyer, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'buyer': buyer,
            })
        if boss_task.type == 'rt':
            renter = boss_task.new_renter
            form = forms.CombinedRenterStatusForm(renter_instance=renter, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'renter': renter,
            })
        if boss_task.type == 'ps':
            person = boss_task.new_person
            form = forms.CombinedPersonStatusForm(person_instance=person, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'person': person,
            })
        if boss_task.type == 'ss':
            session = boss_task.new_session
            form = forms.CombinedSessionStatusForm(session_instance=session, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'session': session,
            })
        if boss_task.type == 'rs':
            result_session = boss_task.result_session
            form = forms.CombinedSessionResultForm(result_session_instance=result_session, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'result_session': result_session,
            })

    def post(self, request, pk, code):
        boss_task = get_object_or_404(models.TaskBoss, pk=pk, code=code)
        if boss_task.type == 'sf':
            sale_file = boss_task.new_sale_file
            form = forms.CombinedSaleFileStatusForm(request.POST, sale_file_instance=sale_file, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'sale_file': sale_file,
            })
        if boss_task.type == 'rf':
            rent_file = boss_task.new_rent_file
            form = forms.CombinedRentFileStatusForm(request.POST, rent_file_instance=rent_file, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'rent_file': rent_file,
            })
        if boss_task.type == 'by':
            buyer = boss_task.new_buyer
            form = forms.CombinedBuyerStatusForm(request.POST, buyer_instance=buyer, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'buyer': buyer,
            })
        if boss_task.type == 'rt':
            renter = boss_task.new_renter
            form = forms.CombinedRenterStatusForm(request.POST, renter_instance=renter, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'renter': renter,
            })
        if boss_task.type == 'ps':
            person = boss_task.new_person
            form = forms.CombinedPersonStatusForm(request.POST, person_instance=person, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'person': person,
            })
        if boss_task.type == 'ss':
            session = boss_task.new_session
            form = forms.CombinedSessionStatusForm(request.POST, session_instance=session, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'session': session,
            })
        if boss_task.type == 'rs':
            result_session = boss_task.result_session
            form = forms.CombinedSessionResultForm(request.POST, result_session_instance=result_session,
                                                   boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'result_session': result_session,
            })


class TaskBossDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.TaskBoss
    template_name = 'dashboard/boss/boss_task_delete.html'
    success_url = reverse_lazy('boss_task_list')
    context_object_name = 'task'
    permission_model = 'TaskBoss'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "وظیفه مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


def delete_request_list_view(request):
    context = {}
    querysets = {
        'sale_files': models.SaleFile.objects.filter(delete_request='Yes'),
        'rent_files': models.RentFile.objects.filter(delete_request='Yes'),
        'buyers': models.Buyer.objects.filter(delete_request='Yes'),
        'renters': models.Renter.objects.filter(delete_request='Yes'),
        'persons': models.Person.objects.filter(delete_request='Yes'),
    }

    all_items = []
    for item in querysets['sale_files']:
        item.model_type = 'sale_file'
        all_items.append(item)
    for item in querysets['rent_files']:
        item.model_type = 'rent_file'
        all_items.append(item)
    for item in querysets['buyers']:
        item.model_type = 'buyer'
        all_items.append(item)
    for item in querysets['renters']:
        item.model_type = 'renter'
        all_items.append(item)
    for item in querysets['persons']:
        item.model_type = 'person'
        all_items.append(item)

    try:
        all_items.sort(key=attrgetter('created_at'), reverse=True)
    except AttributeError:
        try:
            all_items.sort(key=attrgetter('id'), reverse=True)
        except AttributeError:
            pass

    # Pagination
    paginator = Paginator(all_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    paginated_sale_files = []
    paginated_rent_files = []
    paginated_buyers = []
    paginated_renters = []
    paginated_persons = []

    for item in page_obj:
        if hasattr(item, 'model_type'):
            if item.model_type == 'sale_file':
                paginated_sale_files.append(item)
            elif item.model_type == 'rent_file':
                paginated_rent_files.append(item)
            elif item.model_type == 'buyer':
                paginated_buyers.append(item)
            elif item.model_type == 'renter':
                paginated_renters.append(item)
            elif item.model_type == 'person':
                paginated_persons.append(item)

    if paginated_sale_files:
        context['sale_files'] = paginated_sale_files
    if paginated_rent_files:
        context['rent_files'] = paginated_rent_files
    if paginated_buyers:
        context['buyers'] = paginated_buyers
    if paginated_renters:
        context['renters'] = paginated_renters
    if paginated_persons:
        context['persons'] = paginated_persons

    context['page_obj'] = page_obj
    return render(request, 'dashboard/boss/delete_item_list.html', context)


# --------------------------------- Reports --------------------------------
class ReportCreateView(LoginRequiredMixin, CreateView):
    model = models.Report
    form_class = forms.ReportForm
    template_name = 'dashboard/reports/report_create.html'
    success_url = reverse_lazy('current_month')

    def dispatch(self, request, *args, **kwargs):
        now = timezone.now()
        today = datetime2jalali(now)
        today = today.strftime('%Y/%m/%d')
        # user_today_report = models.Report.objects.filter(agent=request.user).filter(date=today)
        # if user_today_report:
        #     raise PermissionDenied("گزارش امروز شما موجود است و اجازه دسترسی مجدد ندارید.")
        if models.Report.objects.filter(agent=request.user).filter(date=today):
            raise PermissionDenied("گزارش امروز شما موجود است و اجازه دسترسی مجدد ندارید.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['formset'] = forms.ReportItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = forms.ReportItemFormSet(instance=self.object)

        now = timezone.now()
        today = datetime2jalali(now)
        context['today'] = today.strftime('%Y/%m/%d')
        context['page_title'] = 'ایجاد گزارش روزانه جدید'
        context['submit_text'] = 'ثبت گزارش'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.agent = self.request.user
            self.object.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                messages.success(self.request, 'گزارش با موفقیت ثبت شد.')
                return redirect(self.success_url)
            else:
                return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'لطفا خطاهای فرم را بررسی کنید.')
        return super().form_invalid(form)


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Report
    form_class = forms.ReportForm
    template_name = 'dashboard/reports/report_create.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        agent_pk = self.kwargs.get('agent_pk')
        date = self.kwargs.get('date')
        try:
            obj = queryset.get(agent__pk=agent_pk, date=date)
        except models.Report.DoesNotExist:
            raise Http404("گزارش روزانه یافت نشد")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = forms.ReportItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = forms.ReportItemFormSet(instance=self.object)
        context['page_title'] = 'ویرایش گزارش روزانه'
        context['submit_text'] = 'بروزرسانی گزارش'
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save()
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
                messages.success(self.request, 'گزارش روزانه با موفقیت بروزرسانی شد.')
                return redirect(self.get_success_url())
            else:
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('report_detail', kwargs={'agent_pk': self.object.agent.pk, 'date': self.object.date})


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = models.Report
    template_name = 'dashboard/reports/report_detail.html'
    context_object_name = 'report'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        agent_pk = self.kwargs.get('agent_pk')
        date = self.kwargs.get('date')
        try:
            obj = queryset.get(agent__pk=agent_pk, date=date)
        except models.Report.DoesNotExist:
            raise Http404("گزارش روزانه یافت نشد")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_items'] = self.object.ads.all()
        return context


class ReportListView(ReadOnlyPermissionMixin, ListView):
    model = models.Report
    template_name = 'dashboard/reports/report_list.html'
    context_object_name = 'reports'
    permission_model = 'Report'

    def dispatch(self, request, *args, **kwargs):
        if request.user.title != 'bs':
            raise PermissionDenied("فقط مدیر اجازه دسترسی به این صفحه را دارد")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        date = self.kwargs.get('date')
        return models.Report.objects.filter(
            date=date
        ).select_related(
            'agent',
            'agent__sub_district',
            'agent__sub_district__district',
            'agent__sub_district__district__city',
            'agent__sub_district__district__city__province'
        ).order_by('agent__sub_district', 'agent__name_family')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = self.kwargs.get('date')

        reports_by_sub_district = defaultdict(list)
        for report in self.object_list:
            if report.agent and report.agent.sub_district:
                sub_district_name = report.agent.sub_district.name
                reports_by_sub_district[sub_district_name].append(report)
            else:
                reports_by_sub_district['بدون زیرمحله'].append(report)
        reports_by_sub_district = dict(sorted(reports_by_sub_district.items()))

        agents_with_reports = set(self.object_list.values_list('agent_id', flat=True))
        all_agents = models.CustomUserModel.objects.filter(
            is_active=True
        ).exclude(
            title='bs'
        ).select_related('sub_district')

        # Find agents without reports
        agents_without_reports = []
        for agent in all_agents:
            if agent.id not in agents_with_reports:
                display_name = agent.name_family if agent.name_family else agent.username
                title_display = agent.get_title_display() if agent.title else 'نامشخص'
                agents_without_reports.append({
                    'id': agent.id,
                    'display_name': display_name,
                    'title': title_display,
                    'full_info': f"{display_name} - {title_display}"
                })

        context['reports_by_sub_district'] = reports_by_sub_district
        context['date'] = date
        context['total_reports'] = self.object_list.count()
        context['agents_without_reports'] = agents_without_reports
        context['missing_reports_count'] = len(agents_without_reports)
        return context


# --------------------------------- Services --------------------------------
class SessionListView(ReadOnlyPermissionMixin, ListView):
    model = models.Session
    template_name = 'dashboard/services/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 6
    permission_model = 'Session'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = (models.Session.objects
                        .select_related('agent', 'agent__sub_district', 'sale_file', 'rent_file', 'buyer', 'renter').all())
            form = forms.ServiceFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['type']:
                    queryset_filtered = queryset_filtered.filter(type=form.cleaned_data['type'])
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset
        else:
            if not self.request.user.sub_district:
                return models.Session.objects.none()

            user_sub_district = self.request.user.sub_district
            sale_sessions = models.Session.objects.filter(
                sale_file_code__isnull=False,
                sale_file_code__in=models.SaleFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            rent_sessions = models.Session.objects.filter(
                rent_file_code__isnull=False,
                rent_file_code__in=models.RentFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            queryset = (sale_sessions | rent_sessions).distinct()
            queryset = queryset.filter(agent=self.request.user)
            form = forms.ServiceFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['type']:
                    queryset_filtered = queryset_filtered.filter(type=form.cleaned_data['type'])
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered

            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.ServiceFilterForm(self.request.GET)
        context['filter_form'] = form
        return context


class SessionCreateView(PermissionRequiredMixin, CreateView):
    model = models.Session
    form_class = forms.SessionCreateForm
    template_name = 'dashboard/services/session_create.html'
    permission_model = 'Session'
    permission_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        sale_file_code = self.request.GET.get('sale_file_code')
        if sale_file_code:
            kwargs['sale_file_code'] = sale_file_code
        rent_file_code = self.request.GET.get('rent_file_code')
        if rent_file_code:
            kwargs['rent_file_code'] = rent_file_code
        buyer_code = self.request.GET.get('buyer_code')
        if buyer_code:
            kwargs['buyer_code'] = buyer_code
        renter_code = self.request.GET.get('renter_code')
        if renter_code:
            kwargs['renter_code'] = renter_code
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_file_code = self.request.GET.get('sale_file_code')
        if sale_file_code:
            try:
                sale_file = models.SaleFile.objects.get(code=sale_file_code)
                context['sale_file'] = sale_file
                context['pre_selected_sale_file'] = True
            except models.SaleFile.DoesNotExist:
                pass
        rent_file_code = self.request.GET.get('rent_file_code')
        if rent_file_code:
            try:
                rent_file = models.RentFile.objects.get(code=rent_file_code)
                context['rent_file'] = rent_file
                context['pre_selected_rent_file'] = True
            except models.RentFile.DoesNotExist:
                pass
        buyer_code = self.request.GET.get('buyer_code')
        if buyer_code:
            try:
                buyer = models.Buyer.objects.get(code=buyer_code)
                context['buyer'] = buyer
                context['pre_selected_buyer'] = True
            except models.Buyer.DoesNotExist:
                pass
        renter_code = self.request.GET.get('renter_code')
        if renter_code:
            try:
                renter = models.Renter.objects.get(code=renter_code)
                context['renter'] = renter
                context['pre_selected_renter'] = True
            except models.Renter.DoesNotExist:
                pass
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "نشست جدید در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('session_list')


class SessionUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Session
    form_class = forms.SessionCreateForm
    template_name = 'dashboard/services/session_update.html'
    context_object_name = 'session'
    permission_model = 'Session'
    permission_action = 'update'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('session_list')


class SessionDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Session
    template_name = 'dashboard/services/session_delete.html'
    success_url = reverse_lazy('session_list')
    context_object_name = 'session'
    permission_model = 'Session'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "نشست مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class SessionDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Session
    context_object_name = 'session'
    template_name = 'dashboard/services/session_detail.html'
    permission_model = 'Session'

    def get_queryset(self):
        return models.Session.objects.select_related(
            'agent',
            'agent__sub_district',
            'agent__sub_district__district',
            'agent__sub_district__district__city',
            'agent__sub_district__district__city__province',
            'sale_file',
            'rent_file',
            'buyer',
            'renter',
        )


class SessionResultView(PermissionRequiredMixin, UpdateView):
    model = models.Session
    form_class = forms.SessionResultForm
    template_name = 'dashboard/services/session_result.html'
    context_object_name = 'session'
    permission_model = 'Session'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (و توسط مدیر مشاهده خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('session_list')


class TradeListView(ReadOnlyPermissionMixin, ListView):
    model = models.Trade
    template_name = 'dashboard/services/trade_list.html'
    context_object_name = 'trades'
    paginate_by = 6
    permission_model = 'Trade'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Trade.objects.select_related('session', 'session__agent', 'session__agent__sub_district',
                                                           'session__sale_file', 'session__rent_file', 'session__buyer',
                                                           'session__renter').all()
            form = forms.TradeFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['type']:
                    queryset_filtered = queryset_filtered.filter(type=form.cleaned_data['type'])
                if form.cleaned_data['followup_code_status']:
                    queryset_filtered = queryset_filtered.filter(
                        followup_code_status=form.cleaned_data['followup_code_status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset
        else:
            if not self.request.user.sub_district:
                return models.Trade.objects.none()

            user_sub_district = self.request.user.sub_district
            sale_trades = models.Trade.objects.filter(
                session__sale_file_code__isnull=False,
                session__sale_file_code__in=models.SaleFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            rent_trades = models.Trade.objects.filter(
                session__rent_file_code__isnull=False,
                session__rent_file_code__in=models.RentFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            queryset = (sale_trades | rent_trades).distinct()
            queryset = queryset.filter(session__agent=self.request.user)
            form = forms.TradeFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['type']:
                    queryset_filtered = queryset_filtered.filter(type=form.cleaned_data['type'])
                if form.cleaned_data['followup_code_status']:
                    queryset_filtered = queryset_filtered.filter(
                        followup_code_status=form.cleaned_data['followup_code_status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered

            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TradeFilterForm(self.request.GET)
        context['filter_form'] = form
        return context


class TradeCreateView(PermissionRequiredMixin, CreateView):
    model = models.Trade
    form_class = forms.TradeCreateForm
    template_name = 'dashboard/services/trade_create.html'
    permission_model = 'Trade'
    permission_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "نشست جدید در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('trade_list')


class TradeUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Trade
    form_class = forms.TradeCreateForm
    template_name = 'dashboard/services/trade_update.html'
    context_object_name = 'trade'
    permission_model = 'Trade'
    permission_action = 'update'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('trade_list')


class TradeDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Trade
    context_object_name = 'trade'
    template_name = 'dashboard/services/trade_detail.html'
    permission_model = 'Trade'


class TradeCodeView(PermissionRequiredMixin, UpdateView):
    model = models.Trade
    form_class = forms.TradeCodeForm
    template_name = 'dashboard/services/trade_code.html'
    context_object_name = 'trade'
    permission_model = 'Trade'
    permission_action = 'update'

    def form_valid(self, form):
        trade = form.save(commit=False)
        trade.followup_code_status = 'tkn'
        trade.save()
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (و توسط مدیر مشاهده خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('trade_list')


# -------------------------------- Calendar -------------------------------
def calendar_current_month_view(request):
    user = request.user
    now = timezone.now()
    today = datetime2jalali(now)
    month = functions.current_month()
    current_month = functions.current_month_finder(today.month)
    previous_month = functions.previous_month_finder(today.month)
    previous_2_month = functions.previous_2_month_finder(today.month)
    next_month = functions.next_month_finder(today.month)
    next_2_month = functions.next_2_month_finder(today.month)

    # Reports
    user_reports = models.Report.objects.filter(
        agent=user
    ).values_list('date', flat=True)
    report_dates = set(user_reports)
    days_data = []
    today_str = today.strftime('%Y/%m/%d')
    for day in month:
        day_info = {
            'date': day,
            'weekday': None,
            'is_today': day == today_str,
            'is_past': day < today_str,
            'is_future': day > today_str,
            'has_report': day in report_dates,
        }
        days_data.append(day_info)
    context = {
        'user': user,
        'today': today_str,
        'month': month,
        'days_data': days_data,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }
    return render(request, 'dashboard/calendar/current.html', context=context)


def calendar_previous_month_view(request):
    user = request.user
    now = timezone.now()
    today = datetime2jalali(now)
    month = functions.previous_month()
    current_month = functions.current_month_finder(today.month)
    previous_month = functions.previous_month_finder(today.month)
    previous_2_month = functions.previous_2_month_finder(today.month)
    next_month = functions.next_month_finder(today.month)
    next_2_month = functions.next_2_month_finder(today.month)

    # Reports
    user_reports = models.Report.objects.filter(
        agent=user
    ).values_list('date', flat=True)
    report_dates = set(user_reports)
    days_data = []
    today_str = today.strftime('%Y/%m/%d')
    for day in month:
        day_info = {
            'date': day,
            'weekday': None,
            'is_today': day == today_str,
            'is_past': day < today_str,
            'is_future': day > today_str,
            'has_report': day in report_dates,
        }
        days_data.append(day_info)

    context = {
        'user': user,
        'today': today_str,
        'month': month,
        'days_data': days_data,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }
    return render(request, 'dashboard/calendar/previous.html', context=context)


def calendar_previous_2_month_view(request):
    user = request.user
    now = timezone.now()
    today = datetime2jalali(now)
    month = functions.previous_2_month()
    current_month = functions.current_month_finder(today.month)
    previous_month = functions.previous_month_finder(today.month)
    previous_2_month = functions.previous_2_month_finder(today.month)
    next_month = functions.next_month_finder(today.month)
    next_2_month = functions.next_2_month_finder(today.month)

    # Reports
    user_reports = models.Report.objects.filter(
        agent=user
    ).values_list('date', flat=True)
    report_dates = set(user_reports)
    days_data = []
    today_str = today.strftime('%Y/%m/%d')
    for day in month:
        day_info = {
            'date': day,
            'weekday': None,
            'is_today': day == today_str,
            'is_past': day < today_str,
            'is_future': day > today_str,
            'has_report': day in report_dates,
        }
        days_data.append(day_info)

    context = {
        'user': user,
        'today': today_str,
        'month': month,
        'days_data': days_data,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }
    return render(request, 'dashboard/calendar/2previous.html', context=context)


def calendar_next_month_view(request):
    user = request.user
    now = timezone.now()
    today = datetime2jalali(now)
    month = functions.next_month()
    current_month = functions.current_month_finder(today.month)
    previous_month = functions.previous_month_finder(today.month)
    previous_2_month = functions.previous_2_month_finder(today.month)
    next_month = functions.next_month_finder(today.month)
    next_2_month = functions.next_2_month_finder(today.month)

    days_data = []
    today_str = today.strftime('%Y/%m/%d')
    for day in month:
        day_info = {
            'date': day,
            'weekday': None,
            'is_today': day == today_str,
            'is_past': day < today_str,
            'is_future': day > today_str,
            'has_report': False,
        }
        days_data.append(day_info)

    context = {
        'user': user,
        'today': today_str,
        'month': month,
        'days_data': days_data,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }
    return render(request, 'dashboard/calendar/next.html', context=context)


def calendar_next_2_month_view(request):
    user = request.user
    now = timezone.now()
    today = datetime2jalali(now)
    month = functions.next_2_month()
    current_month = functions.current_month_finder(today.month)
    previous_month = functions.previous_month_finder(today.month)
    previous_2_month = functions.previous_2_month_finder(today.month)
    next_month = functions.next_month_finder(today.month)
    next_2_month = functions.next_2_month_finder(today.month)

    days_data = []
    today_str = today.strftime('%Y/%m/%d')
    for day in month:
        day_info = {
            'date': day,
            'weekday': None,
            'is_today': day == today_str,
            'is_past': day < today_str,
            'is_future': day > today_str,
            'has_report': False,
        }
        days_data.append(day_info)

    context = {
        'user': user,
        'today': today_str,
        'month': month,
        'days_data': days_data,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }
    return render(request, 'dashboard/calendar/2next.html', context=context)


# ------------------------------- Interactions ------------------------------
class AnnouncementListView(LoginRequiredMixin, ListView):
    model = models.Announcement
    template_name = 'dashboard/interactions/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        base_qs = models.Announcement.objects.filter(
            visible_to=self.request.user,
            is_active=True
        ).select_related(
            'created_by',
            'content_type'
        ).prefetch_related(
            'viewed_by'
        ).order_by('-datetime_created')

        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'sf':
            return base_qs.filter(announcement_type='sf').order_by('-datetime_created')
        elif filter_type == 'rf':
            return base_qs.filter(announcement_type='rf').order_by('-datetime_created')
        elif filter_type == 'by':
            return base_qs.filter(announcement_type='by').order_by('-datetime_created')
        elif filter_type == 'rt':
            return base_qs.filter(announcement_type='rt').order_by('-datetime_created')
        else:
            return base_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'all')
        context['unviewed_count'] = self.get_queryset().exclude(viewed_by=self.request.user).count()
        return context


class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = models.Announcement
    template_name = 'dashboard/interactions/announcement_detail.html'
    context_object_name = 'announcement'

    def get_object(self):
        announcement = super().get_object()
        if self.request.user not in announcement.viewed_by.all():
            announcement.viewed_by.add(self.request.user)
            cache.delete(f'notifications_{self.request.user.pk}')
        return announcement

    def get_already_sent_ids(self, announcement, content_type):
        already_sent_items = models.InteractionItem.objects.filter(
            interaction__announcement=announcement,
            interaction__sender=self.request.user,
            content_type=content_type
        ).values_list('object_id', flat=True)

        return list(already_sent_items)

    def get_suggestions_for_sale_file(self, sale_file):
        suggested_buyers = models.Buyer.objects.select_related(
            'created_by', 'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts'
        ).filter(
            created_by=self.request.user,
            status='acc',
            budget_announced__gt=0.9 * sale_file.price_announced,
            budget_announced__lt=1.1 * sale_file.price_announced,
            area_min__lt=1.2 * sale_file.area,
            area_max__gt=0.8 * sale_file.area
        ).exclude(delete_request='Yes')

        # Exclude already sent buyers
        buyer_content_type = ContentType.objects.get_for_model(models.Buyer)
        already_sent_ids = self.get_already_sent_ids(self.object, buyer_content_type)
        if already_sent_ids:
            suggested_buyers = suggested_buyers.exclude(id__in=already_sent_ids)

        return suggested_buyers

    def get_suggestions_for_rent_file(self, rent_file):
        base_queryset = models.Renter.objects.select_related(
            'created_by', 'province', 'city', 'district'
        ).prefetch_related(
            'sub_districts'
        ).filter(
            created_by=self.request.user
        ).annotate(
            deposit_total_calc=Cast(
                F('deposit_announced') + (100 * F('rent_announced') / 3),
                PositiveBigIntegerField()
            )
        )

        non_convertable_renters = base_queryset.filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=0.8 * rent_file.deposit_announced,
            deposit_announced__lt=1.2 * rent_file.deposit_announced,
            rent_announced__gt=0.8 * rent_file.rent_announced,
            rent_announced__lt=1.2 * rent_file.rent_announced,
            area_min__lt=1.2 * rent_file.area,
            area_max__gt=0.8 * rent_file.area
        ).exclude(delete_request='Yes')

        rent_total_min = 0.8 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
        rent_total_max = 1.2 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))

        convertable_renters = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=rent_total_min,
            deposit_total_calc__lt=rent_total_max,
            area_min__lt=1.2 * rent_file.area,
            area_max__gt=0.8 * rent_file.area
        ).exclude(delete_request='Yes')

        suggested_renters = (non_convertable_renters | convertable_renters).distinct()

        # Exclude already sent renters
        renter_content_type = ContentType.objects.get_for_model(models.Renter)
        already_sent_ids = self.get_already_sent_ids(self.object, renter_content_type)
        if already_sent_ids:
            suggested_renters = suggested_renters.exclude(id__in=already_sent_ids)

        return suggested_renters

    def get_suggestions_for_buyer(self, buyer):
        budget_min = 0.9 * buyer.budget_announced
        budget_max = 1.1 * buyer.budget_announced
        area_min = 0.8 * buyer.area_min
        area_max = 1.2 * buyer.area_max

        suggested_files = models.SaleFile.objects.select_related(
            'created_by', 'sub_district', 'sub_district__district',
            'sub_district__district__city', 'sub_district__district__city__province'
        ).filter(
            created_by=self.request.user,
            status='acc',
            price_announced__gt=budget_min,
            price_announced__lt=budget_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        # Exclude already sent sale files
        sale_file_content_type = ContentType.objects.get_for_model(models.SaleFile)
        already_sent_ids = self.get_already_sent_ids(self.object, sale_file_content_type)
        if already_sent_ids:
            suggested_files = suggested_files.exclude(id__in=already_sent_ids)

        return suggested_files

    def get_suggestions_for_renter(self, renter):
        deposit_min = 0.8 * renter.deposit_announced
        deposit_max = 1.2 * renter.deposit_announced
        rent_min = 0.8 * renter.rent_announced
        rent_max = 1.2 * renter.rent_announced
        area_min = 0.8 * renter.area_min
        area_max = 1.2 * renter.area_max
        renter_total_min = 0.8 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))
        renter_total_max = 1.2 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))

        base_queryset = models.RentFile.objects.select_related(
            'created_by', 'sub_district', 'sub_district__district',
            'sub_district__district__city', 'sub_district__district__city__province'
        ).filter(
            created_by=self.request.user
        ).annotate(
            deposit_total_calc=Cast(
                F('deposit_announced') + (100 * F('rent_announced') / 3),
                PositiveBigIntegerField()
            )
        )

        non_convertable_files = base_queryset.filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=deposit_min,
            deposit_announced__lt=deposit_max,
            rent_announced__gt=rent_min,
            rent_announced__lt=rent_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        convertable_files = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=renter_total_min,
            deposit_total_calc__lt=renter_total_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(delete_request='Yes')

        suggested_files = (non_convertable_files | convertable_files).distinct()

        # Exclude already sent rent files
        rent_file_content_type = ContentType.objects.get_for_model(models.RentFile)
        already_sent_ids = self.get_already_sent_ids(self.object, rent_file_content_type)
        if already_sent_ids:
            suggested_files = suggested_files.exclude(id__in=already_sent_ids)

        return suggested_files

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        announcement = self.object
        suggestions = []
        interaction_type = None

        if announcement.announcement_type == 'sf':
            sale_file = announcement.content_object
            suggestions = self.get_suggestions_for_sale_file(sale_file)
            interaction_type = 'buyers_to_sale_file'
        elif announcement.announcement_type == 'rf':
            rent_file = announcement.content_object
            suggestions = self.get_suggestions_for_rent_file(rent_file)
            interaction_type = 'renters_to_rent_file'
        elif announcement.announcement_type == 'by':
            buyer = announcement.content_object
            suggestions = self.get_suggestions_for_buyer(buyer)
            interaction_type = 'sale_files_to_buyer'
        elif announcement.announcement_type == 'rt':
            renter = announcement.content_object
            suggestions = self.get_suggestions_for_renter(renter)
            interaction_type = 'rent_files_to_renter'

        paginator = Paginator(suggestions, 20)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['suggestions'] = page_obj.object_list
        context['page_obj'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['interaction_type'] = interaction_type
        context['total_suggestions'] = suggestions.count() if hasattr(suggestions, 'count') else len(suggestions)

        return context


class InteractionCreateView(LoginRequiredMixin, CreateView):
    model = models.Interaction
    fields = []

    def post(self, request, *args, **kwargs):
        announcement_id = self.kwargs.get('announcement_id')
        announcement = get_object_or_404(
            models.Announcement,
            pk=announcement_id,
            visible_to=request.user
        )

        selected_ids = request.POST.getlist('selected_suggestions')
        message = request.POST.get('message', '')
        if not selected_ids:
            messages.error(request, 'لطفاً حداقل یک پیشنهاد را انتخاب کنید.')
            return redirect('announcement_detail', pk=announcement_id)

        interaction_type_map = {
            'sf': ('buyers_to_sale_file', ContentType.objects.get_for_model(models.Buyer)),
            'rf': ('renters_to_rent_file', ContentType.objects.get_for_model(models.Renter)),
            'by': ('sale_files_to_buyer', ContentType.objects.get_for_model(models.SaleFile)),
            'rt': ('rent_files_to_renter', ContentType.objects.get_for_model(models.RentFile)),
        }
        interaction_type, content_type = interaction_type_map[announcement.announcement_type]

        interaction = models.Interaction.objects.create(
            announcement=announcement,
            sender=request.user,
            receiver=announcement.created_by,
            interaction_type=interaction_type,
            message=message,
            status='sent'
        )

        for suggestion_id in selected_ids:
            suggestion_obj = content_type.model_class().objects.get(pk=suggestion_id)
            if hasattr(suggestion_obj, 'price_announced'):
                cached_price = suggestion_obj.price_announced
            elif hasattr(suggestion_obj, 'deposit_announced'):
                cached_price = suggestion_obj.deposit_announced
            else:
                cached_price = None
            if hasattr(suggestion_obj, 'area'):
                cached_area = suggestion_obj.area
            elif hasattr(suggestion_obj, 'area_min'):
                cached_area = suggestion_obj.area_min
            else:
                cached_area = None

            models.InteractionItem.objects.create(
                interaction=interaction,
                content_object=suggestion_obj,
                cached_price=cached_price,
                cached_area=cached_area
            )
        messages.success(
            request,
            f'پیشنهادات شما ({len(selected_ids)} مورد) با موفقیت ارسال شد.'
        )
        cache.delete(f'notifications_{interaction.receiver.pk}')

        return redirect('interaction_detail', pk=interaction.pk)


class InteractionListView(LoginRequiredMixin, ListView):
    model = models.Interaction
    template_name = 'dashboard/interactions/interaction_list.html'
    context_object_name = 'interactions'
    paginate_by = 20

    def get_queryset(self):
        base_qs = models.Interaction.objects.select_related(
            'sender', 'receiver', 'announcement'
        ).prefetch_related(
            'items'
        )

        filter_type = self.request.GET.get('filter', 'all')
        if filter_type == 'sent':
            return base_qs.filter(sender=self.request.user).order_by('-datetime_created')
        elif filter_type == 'received':
            return base_qs.filter(receiver=self.request.user).order_by('-datetime_created')
        else:
            return base_qs.filter(
                Q(sender=self.request.user) | Q(receiver=self.request.user)
            ).order_by('-datetime_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'all')
        context['unviewed_received_count'] = models.Interaction.objects.filter(
            receiver=self.request.user,
            status='unseen'
        ).count()
        return context


class InteractionDetailView(LoginRequiredMixin, DetailView):
    model = models.Interaction
    template_name = 'dashboard/interactions/interaction_detail.html'
    context_object_name = 'interaction'

    def get_queryset(self):
        return models.Interaction.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).select_related(
            'sender', 'receiver', 'announcement'
        ).prefetch_related(
            'items__content_type',
            'items__content_object'
        )

    def get_object(self):
        interaction = super().get_object()
        if interaction.receiver == self.request.user and interaction.status == 'sent':
            interaction.status = 'viewed'
            interaction.datetime_viewed = timezone.now()
            interaction.save(update_fields=['status', 'datetime_viewed'])
            cache.delete(f'notifications_{self.request.user.pk}')
        return interaction

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcement_object'] = self.object.announcement.content_object
        return context


# ------------------------------- DailyTasks ------------------------------
class NotifiedTaskListView(LoginRequiredMixin, ListView):
    model = models.NotifiedTask
    template_name = 'dashboard/tasks/notified_task_list.html'
    context_object_name = 'all_tasks'

    def get_queryset(self):
        return (models.NotifiedTask.objects.filter(agent=self.request.user)
                .select_related(
            'related_announcement',
            'related_interaction_item',
            'related_interaction_item__interaction__sender',
            'content_type'
        )
                .prefetch_related(
            'related_announcement__content_object',
            'related_interaction_item__content_object'
        )
                .order_by('status', '-created_at'))

    def _calculate_stats(self, agent, days):
        base_qs = models.NotifiedTask.objects.filter(
            agent=agent,
            created_at__gte=timezone.now() - timedelta(days=days)
        )

        # Single query to get all counts
        stats = base_qs.aggregate(
            # All tasks
            all_count=Count('id'),
            all_waiting=Count('id', filter=Q(status='waiting')),
            all_done=Count('id', filter=Q(status='done')),

            # Suggestion tasks
            suggestion_count=Count('id', filter=Q(task_type='announcement_suggestions')),
            suggestion_waiting=Count('id', filter=Q(task_type='announcement_suggestions', status='waiting')),
            suggestion_done=Count('id', filter=Q(task_type='announcement_suggestions', status='done')),

            # Interaction tasks
            interaction_count=Count('id', filter=Q(task_type='received_interaction')),
            interaction_waiting=Count('id', filter=Q(task_type='received_interaction', status='waiting')),
            interaction_done=Count('id', filter=Q(task_type='received_interaction', status='done')),
        )

        # Calculate percentages
        def calculate_percentage(part, total):
            return round(100 * (part / total), 1) if total != 0 else '-'

        return {
            'all_tasks_all_statuses': stats['all_count'],
            'all_tasks_waiting': stats['all_waiting'],
            'all_tasks_done': stats['all_done'],
            'all_tasks_done_percentage': calculate_percentage(stats['all_done'], stats['all_count']),

            'suggestion_tasks_all_statuses': stats['suggestion_count'],
            'suggestion_tasks_waiting': stats['suggestion_waiting'],
            'suggestion_tasks_done': stats['suggestion_done'],
            'suggestion_tasks_done_percentage': calculate_percentage(stats['suggestion_done'],
                                                                     stats['suggestion_count']),

            'interaction_tasks_all_statuses': stats['interaction_count'],
            'interaction_tasks_waiting': stats['interaction_waiting'],
            'interaction_tasks_done': stats['interaction_done'],
            'interaction_tasks_done_percentage': calculate_percentage(stats['interaction_done'],
                                                                      stats['interaction_count']),
        }

    def _get_basic_counts(self, agent):
        counts = models.NotifiedTask.objects.filter(agent=agent).aggregate(
            announcement_tasks_count=Count('id', filter=Q(task_type='announcement_suggestions')),
            waiting_received_tasks_count=Count('id', filter=Q(task_type='received_interaction', status='waiting')),
            waiting_suggested_tasks_count=Count('id', filter=Q(task_type='announcement_suggestions', status='waiting')),
            all_waiting_count=Count('id', filter=Q(status='waiting')),
        )

        return counts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agent = self.request.user

        # Get all tasks with optimized queryset
        all_tasks = self.get_queryset()

        # Filter tasks in Python to avoid additional DB queries
        all_tasks_list = list(all_tasks)
        context['announcement_tasks'] = [task for task in all_tasks_list if
                                         task.task_type == 'announcement_suggestions']
        context['received_tasks'] = [task for task in all_tasks_list if task.task_type == 'received_interaction']

        # Get basic counts in single query
        basic_counts = self._get_basic_counts(agent)
        context['announcement_tasks_count'] = basic_counts['announcement_tasks_count']
        context['waiting_received_tasks_count'] = basic_counts['waiting_received_tasks_count']
        context['waiting_suggested_tasks_count'] = basic_counts['waiting_suggested_tasks_count']

        # Date information
        today = jdatetime.date.today()
        context['today'] = today.strftime('%Y/%m/%d')
        context['today_display'] = today.strftime('%A، %d %B %Y')
        context['is_friday'] = today.weekday() == 6
        if not context['is_friday']:
            context['daily_status'] = models.DailyTaskStatus.get_or_create_for_today(self.request.user)

        # Calculate stats for 10 and 30 days in single queries
        stats_10 = self._calculate_stats(agent, 10)
        stats_30 = self._calculate_stats(agent, 30)

        # Add 10-day stats to context
        for key, value in stats_10.items():
            context[f"{key}_10"] = value

        # Add 30-day stats to context
        for key, value in stats_30.items():
            context[f"{key}_30"] = value

        # Fix the typo in the original code
        if context.get('suggestion_tasks_done_percentage_30') == '-':
            context['all_tasks_done_percentage_30'] = '-'

        # Additional counts for notifications (optimized)
        from django.db.models import Count, Q, Exists, OuterRef

        # Announcement count
        announcement_count = models.Announcement.objects.filter(
            is_active=True,
            visible_to=agent
        ).exclude(
            viewed_by=agent
        ).count()
        context['unseen_announcements_count'] = announcement_count

        # Interaction count
        interaction_count = models.Interaction.objects.filter(
            receiver=agent,
            status='sent'
        ).count()
        context['unseen_interactions_count'] = interaction_count

        # Waiting tasks count
        context['waiting_tasks_count'] = basic_counts['all_waiting_count']

        # Sub_district (if needed)
        if hasattr(agent, 'sub_district') and agent.sub_district:
            # This will use the cached relation if available
            context['agent_subdistrict'] = agent.sub_district

        return context


class NotifiedTaskDetailView(LoginRequiredMixin, DetailView):
    model = models.NotifiedTask
    template_name = 'dashboard/tasks/notified_task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return models.NotifiedTask.objects.filter(
            agent=self.request.user
        ).select_related(
            'related_announcement',
            'related_interaction_item',
            'related_interaction_item__interaction',
            'related_interaction_item__interaction__sender',
            'content_type'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.content_object:
            context['related_object'] = self.object.content_object
        if self.object.related_announcement:
            context['announcement_object'] = self.object.related_announcement.content_object
            context['all_suggestions'] = self.object.related_announcement.get_suggestions_for_agent(self.request.user)
        if self.object.related_interaction_item:
            context['interaction'] = self.object.related_interaction_item.interaction
            context['sender'] = self.object.related_interaction_item.interaction.sender
        return context


class BossAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.title == 'bs'


class BossAgentTaskListView(LoginRequiredMixin, BossAccessMixin, ListView):
    model = models.CustomUserModel
    template_name = 'dashboard/tasks/boss_agent_task_list.html'
    context_object_name = 'agents_by_district'

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        agents = models.CustomUserModel.objects.filter(
            title__in=['fp', 'cp', 'bt', 'nd']
        ).select_related('sub_district').annotate(
            total_tasks=Count('notified_tasks', filter=Q(notified_tasks__created_at__gte=thirty_days_ago)),
            waiting_tasks=Count('notified_tasks', filter=Q(notified_tasks__status='waiting',
                                                           notified_tasks__created_at__gte=thirty_days_ago)),
            done_tasks=Count('notified_tasks',
                             filter=Q(notified_tasks__status='done', notified_tasks__created_at__gte=thirty_days_ago)),
            done_percentage=Case(
                When(total_tasks=0, then=0.0),
                default=Cast(F('done_tasks'), FloatField()) * 100.0 / Cast(F('total_tasks'), FloatField()),
                output_field=FloatField()
            )
        ).order_by('sub_district__name', 'name_family')

        return agents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Organize agents by sub_district
        agents = self.get_queryset()
        agents_by_district = {}

        for agent in agents:
            district_name = agent.sub_district.name if agent.sub_district else 'بدون محله'
            if district_name not in agents_by_district:
                agents_by_district[district_name] = []
            agents_by_district[district_name].append(agent)

        context['agents_by_district'] = agents_by_district

        # Overall statistics
        context['total_agents'] = agents.count()
        context['total_waiting_tasks'] = sum(agent.waiting_tasks for agent in agents)

        return context


class BossAgentTaskDetailView(LoginRequiredMixin, BossAccessMixin, TemplateView):
    template_name = 'dashboard/tasks/boss_agent_task_detail.html'

    def get_agent_queryset(self, agent):
        return (models.NotifiedTask.objects.filter(agent=agent)
                .select_related(
            'related_announcement',
            'related_interaction_item',
            'related_interaction_item__interaction__sender',
            'content_type'
        )
                .prefetch_related(
            'related_announcement__content_object',
            'related_interaction_item__content_object'
        )
                .order_by('status', '-created_at'))

    def _calculate_stats(self, agent, days):
        base_qs = models.NotifiedTask.objects.filter(
            agent=agent,
            created_at__gte=timezone.now() - timedelta(days=days)
        )

        stats = base_qs.aggregate(
            all_count=Count('id'),
            all_waiting=Count('id', filter=Q(status='waiting')),
            all_done=Count('id', filter=Q(status='done')),
            suggestion_count=Count('id', filter=Q(task_type='announcement_suggestions')),
            suggestion_waiting=Count('id', filter=Q(task_type='announcement_suggestions', status='waiting')),
            suggestion_done=Count('id', filter=Q(task_type='announcement_suggestions', status='done')),
            interaction_count=Count('id', filter=Q(task_type='received_interaction')),
            interaction_waiting=Count('id', filter=Q(task_type='received_interaction', status='waiting')),
            interaction_done=Count('id', filter=Q(task_type='received_interaction', status='done')),
        )

        def calculate_percentage(part, total):
            return round(100 * (part / total), 1) if total != 0 else '-'

        return {
            'all_tasks_all_statuses': stats['all_count'],
            'all_tasks_waiting': stats['all_waiting'],
            'all_tasks_done': stats['all_done'],
            'all_tasks_done_percentage': calculate_percentage(stats['all_done'], stats['all_count']),
            'suggestion_tasks_all_statuses': stats['suggestion_count'],
            'suggestion_tasks_waiting': stats['suggestion_waiting'],
            'suggestion_tasks_done': stats['suggestion_done'],
            'suggestion_tasks_done_percentage': calculate_percentage(stats['suggestion_done'],
                                                                     stats['suggestion_count']),
            'interaction_tasks_all_statuses': stats['interaction_count'],
            'interaction_tasks_waiting': stats['interaction_waiting'],
            'interaction_tasks_done': stats['interaction_done'],
            'interaction_tasks_done_percentage': calculate_percentage(stats['interaction_done'],
                                                                      stats['interaction_count']),
        }

    def _get_basic_counts(self, agent):
        counts = models.NotifiedTask.objects.filter(agent=agent).aggregate(
            announcement_tasks_count=Count('id', filter=Q(task_type='announcement_suggestions')),
            waiting_received_tasks_count=Count('id', filter=Q(task_type='received_interaction', status='waiting')),
            waiting_suggested_tasks_count=Count('id', filter=Q(task_type='announcement_suggestions', status='waiting')),
            all_waiting_count=Count('id', filter=Q(status='waiting')),
        )
        return counts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the agent
        agent = get_object_or_404(
            models.CustomUserModel,
            pk=self.kwargs['agent_pk'],
            title__in=['fp', 'cp', 'bt']
        )
        context['agent'] = agent

        # Get all tasks with optimized queryset
        all_tasks = self.get_agent_queryset(agent)
        all_tasks_list = list(all_tasks)

        context['all_tasks'] = all_tasks_list
        context['announcement_tasks'] = [task for task in all_tasks_list if
                                         task.task_type == 'announcement_suggestions']
        context['received_tasks'] = [task for task in all_tasks_list if task.task_type == 'received_interaction']

        # Get basic counts in single query
        basic_counts = self._get_basic_counts(agent)
        context['announcement_tasks_count'] = basic_counts['announcement_tasks_count']
        context['waiting_received_tasks_count'] = basic_counts['waiting_received_tasks_count']
        context['waiting_suggested_tasks_count'] = basic_counts['waiting_suggested_tasks_count']
        context['waiting_tasks_count'] = basic_counts['all_waiting_count']

        # Date information
        today = jdatetime.date.today()
        context['today'] = today.strftime('%Y/%m/%d')
        context['today_display'] = today.strftime('%A، %d %B %Y')
        context['is_friday'] = today.weekday() == 6

        # Don't include daily_status for boss view
        context['is_boss_view'] = True

        # Calculate stats for 10 and 30 days
        stats_10 = self._calculate_stats(agent, 10)
        stats_30 = self._calculate_stats(agent, 30)

        # Add 10-day stats to context
        for key, value in stats_10.items():
            context[f"{key}_10"] = value

        # Add 30-day stats to context
        for key, value in stats_30.items():
            context[f"{key}_30"] = value

        # Fix the typo in the original code
        if context.get('suggestion_tasks_done_percentage_30') == '-':
            context['all_tasks_done_percentage_30'] = '-'

        # Sub_district (if needed)
        if hasattr(agent, 'sub_district') and agent.sub_district:
            context['agent_subdistrict'] = agent.sub_district

        return context


# AJAX
@require_POST
def complete_received_task(request, task_id):
    task = get_object_or_404(models.NotifiedTask, pk=task_id, agent=request.user, task_type='received_interaction')
    if task.status != 'waiting':
        messages.error(request, 'این وظیفه قبلاً تکمیل شده است.')
        return redirect('notified_task_list')
    form = forms.NotifiedTaskCompletionForm(request.POST, instance=task)
    if form.is_valid():
        result = form.cleaned_data.get('result', '')
        task.mark_as_done(result)
        cache.delete(f'notifications_{request.user.pk}')
        messages.success(request, 'وظیفه با موفقیت تکمیل شد.')
        return redirect('notified_task_list')
    else:
        messages.error(request, 'لطفاً فرم را به درستی پر کنید.')
        return redirect('notified_task_list')


def get_task_count(request):
    if request.user.is_authenticated:
        tasks = models.NotifiedTask.objects.filter(
            agent=request.user
        )
        return JsonResponse({
            'total': tasks.count(),
            'waiting': tasks.filter(status='waiting').count(),
            'done': tasks.filter(status='done').count(),
            'announcement_suggestions': tasks.filter(task_type='announcement_suggestions', status='waiting').count(),
            'received_interaction': tasks.filter(task_type='received_interaction', status='waiting').count(),
        })
    return JsonResponse({'error': 'Unauthorized'}, status=401)


# --------------------------------- Chat ---------------------------------
class ChatRoomListView(LoginRequiredMixin, ListView):
    """
    List all chat rooms for the current user
    """
    model = models.ChatRoom
    template_name = 'dashboard/chat/chat_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        user = self.request.user

        # Get all rooms where user is a participant
        rooms = models.ChatRoom.objects.filter(
            participants=user
        ).prefetch_related(
            'participants',
            'messages'
        ).annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count('messages', filter=~Q(messages__read_by=user) & ~Q(messages__sender=user))
        ).order_by('-last_message_time')

        return rooms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get or create global group - add ALL users
        group, created = models.ChatRoom.objects.get_or_create(
            room_type='group',
            name='گروه عمومی',
            defaults={'description': 'گروه گفتگوی همه کاربران'}
        )
        if user not in group.participants.all():
            group.participants.add(user)

        # Get or create boss channel - add ALL users (bosses can write, all can read)
        channel, created = models.ChatRoom.objects.get_or_create(
            room_type='channel',
            name='کانال مدیران',
            defaults={'description': 'اطلاعیه‌های مدیریت - فقط مدیران می‌توانند پیام ارسال کنند'}
        )
        if user not in channel.participants.all():
            channel.participants.add(user)

        # Categorize rooms
        context['private_rooms'] = context['rooms'].filter(room_type='private')
        context['group_room'] = context['rooms'].filter(room_type='group').first()
        context['channel_room'] = context['rooms'].filter(room_type='channel').first()

        # Get all users for starting new chats
        context['all_users'] = models.CustomUserModel.objects.filter(
            is_active=True
        ).exclude(pk=user.pk).order_by('name_family', 'username')

        return context


class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    """
    Display messages in a specific chat room
    """
    model = models.ChatRoom
    template_name = 'dashboard/chat/chat_room.html'
    context_object_name = 'room'

    def get_queryset(self):
        return models.ChatRoom.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'messages__sender',
            'messages__reply_to',
            'messages__reactions'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.object
        user = self.request.user

        # Get all messages
        messages = room.messages.all().select_related(
            'sender', 'reply_to', 'reply_to__sender'
        ).prefetch_related('reactions__user', 'read_by')

        context['messages'] = messages

        # Mark messages as read
        unread_messages = messages.exclude(sender=user).exclude(read_by=user)
        for msg in unread_messages:
            msg.read_by.add(user)

        # Check if user can send messages in channel
        context['can_send'] = True
        if room.room_type == 'channel' and user.title != 'bs':
            context['can_send'] = False

        # Get other participant for private chats
        if room.room_type == 'private':
            other_participant = room.participants.exclude(pk=user.pk).first()
            context['other_user'] = other_participant

        return context


@login_required
def start_private_chat(request, user_id):
    """
    Start or get existing private chat with another user
    """
    other_user = get_object_or_404(models.CustomUserModel, pk=user_id, is_active=True)
    current_user = request.user

    if other_user == current_user:
        messages.error(request, 'نمی‌توانید با خودتان چت کنید.')
        return redirect('chat_list')

    # Check if chat already exists
    existing_room = models.ChatRoom.objects.filter(
        room_type='private',
        participants=current_user
    ).filter(
        participants=other_user
    ).first()

    if existing_room:
        return redirect('chat_room', pk=existing_room.pk)

    # Create new private chat
    room = models.ChatRoom.objects.create(
        room_type='private',
        created_by=current_user
    )
    room.participants.add(current_user, other_user)

    return redirect('chat_room', pk=room.pk)


@login_required
def send_message(request, room_id):
    """
    Send a message in a chat room (AJAX)
    """
    if request.method == 'POST':
        room = get_object_or_404(models.ChatRoom, pk=room_id, participants=request.user)

        # Check permissions for channel
        if room.room_type == 'channel' and request.user.title != 'bs':
            return JsonResponse({'error': 'شما اجازه ارسال پیام در این کانال را ندارید.'}, status=403)

        content = request.POST.get('content', '').strip()
        message_type = request.POST.get('message_type', 'text')
        reply_to_id = request.POST.get('reply_to')

        if not content and message_type == 'text':
            return JsonResponse({'error': 'محتوای پیام نمی‌تواند خالی باشد.'}, status=400)

        # Create message
        message = models.Message.objects.create(
            room=room,
            sender=request.user,
            message_type=message_type,
            content=content
        )

        # Handle reply
        if reply_to_id:
            try:
                reply_to = models.Message.objects.get(pk=reply_to_id, room=room)
                message.reply_to = reply_to
                message.save()
            except models.Message.DoesNotExist:
                pass

        # Handle file upload
        if 'file' in request.FILES:
            message.file = request.FILES['file']
            message.save()

        # Mark as read by sender
        message.read_by.add(request.user)

        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'content': message.content,
            'sender': message.sender.name_family or message.sender.username,
            'time': message.get_jalali_time()
        })

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)


@login_required
def edit_message(request, message_id):
    """
    Edit a message (AJAX)
    """
    if request.method == 'POST':
        message = get_object_or_404(
            models.Message,
            pk=message_id,
            sender=request.user,
            message_type='text'
        )

        new_content = request.POST.get('content', '').strip()
        if not new_content:
            return JsonResponse({'error': 'محتوای پیام نمی‌تواند خالی باشد.'}, status=400)

        message.content = new_content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()

        return JsonResponse({
            'success': True,
            'content': message.content,
            'edited': True
        })

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)


@login_required
def delete_message(request, message_id):
    """
    Delete a message (AJAX)
    """
    if request.method == 'POST':
        message = get_object_or_404(models.Message, pk=message_id, sender=request.user)
        message.delete()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)


@login_required
def forward_message(request, message_id):
    """
    Forward a message to another room (AJAX)
    """
    if request.method == 'POST':
        original_message = get_object_or_404(models.Message, pk=message_id)
        target_room_id = request.POST.get('target_room_id')

        target_room = get_object_or_404(
            models.ChatRoom,
            pk=target_room_id,
            participants=request.user
        )

        # Check channel permissions
        if target_room.room_type == 'channel' and request.user.title != 'bs':
            return JsonResponse({'error': 'شما اجازه ارسال پیام در این کانال را ندارید.'}, status=403)

        # Create forwarded message
        forwarded = models.Message.objects.create(
            room=target_room,
            sender=request.user,
            message_type=original_message.message_type,
            content=original_message.content,
            file=original_message.file,
            forwarded_from=original_message
        )
        forwarded.read_by.add(request.user)

        return JsonResponse({
            'success': True,
            'message': 'پیام با موفقیت فوروارد شد.'
        })

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)


@login_required
def add_reaction(request, message_id):
    """
    Add emoji reaction to a message (AJAX)
    """
    if request.method == 'POST':
        message = get_object_or_404(models.Message, pk=message_id)
        emoji = request.POST.get('emoji')

        if not emoji:
            return JsonResponse({'error': 'ایموجی انتخاب نشده است.'}, status=400)

        # Toggle reaction
        reaction, created = models.MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )

        if not created:
            reaction.delete()
            return JsonResponse({'success': True, 'action': 'removed'})

        return JsonResponse({'success': True, 'action': 'added'})

    return JsonResponse({'error': 'متد نامعتبر'}, status=405)


