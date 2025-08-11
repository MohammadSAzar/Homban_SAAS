from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter

from jalali_date import datetime2jalali
from django.utils import timezone

from . import models, forms, functions
from .permissions import PermissionRequiredMixin, ReadOnlyPermissionMixin


# ----------------------------------- Bases -----------------------------------
def home_view(request):
    return render(request, 'dashboard/home.html')


def dashboard_view(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'dashboard/dashboard.html', context)


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
        if self.request.user.title != 'bs':
            sub_district = self.request.user.sub_district
            queryset_default = (
                models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
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
            queryset_default = (models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
                                .filter(status='acc').exclude(delete_request='Yes'))
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
        if self.request.user.title == 'fp':
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
        return context


class SaleFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'dashboard/files/sale_file_detail.html'
    permission_model = 'SaleFile'

    def dispatch(self, request, *args, **kwargs):
        sale_file = self.get_object()
        user = request.user
        if user.title != 'bs' and sale_file.delete_request == 'Yes':
            raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)


class SaleFileGalleryView(DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'dashboard/files/sale_file_gallery.html'


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
        if self.request.user.title != 'bs':
            sub_district = self.request.user.sub_district
            queryset_default = (
                models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
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
            queryset_default = (models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
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
        if self.request.user.title == 'fp':
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
        return context


class RentFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    template_name = 'dashboard/files/rent_file_detail.html'
    permission_model = 'RentFile'

    def dispatch(self, request, *args, **kwargs):
        rent_file = self.get_object()
        user = request.user
        if user.title != 'bs' and rent_file.delete_request == 'Yes':
            raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)


class RentFileGalleryView(DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    template_name = 'dashboard/files/rent_file_gallery.html'


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
        if self.request.user.title == 'bs':
            queryset_default = models.Buyer.objects.select_related('province', 'city', 'district').prefetch_related(
                'sub_districts').exclude(delete_request='Yes')

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

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = ((
                models.Buyer.objects.select_related('province', 'city', 'district').prefetch_related('sub_districts')
                .filter(sub_districts__name__contains=self.request.user.sub_district.name))
                                .exclude(delete_request='Yes').distinct())

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

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.BuyerFilterForm(self.request.GET)

        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))

        context['filter_form'] = form
        return context


class BuyerDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Buyer
    context_object_name = 'buyer'
    template_name = 'dashboard/people/buyer_detail.html'
    permission_model = 'Buyer'

    def dispatch(self, request, *args, **kwargs):
        buyer = self.get_object()
        user = request.user
        if user.title != 'bs' and buyer.delete_request == 'Yes':
            raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)


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
        if self.request.user.title == 'bs':
            queryset_default = models.Renter.objects.select_related('province', 'city', 'district').prefetch_related(
                'sub_districts').exclude(delete_request='Yes')

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

                return queryset_filtered
            return queryset_default
        else:
            queryset_default = (models.Renter.objects.select_related('province', 'city', 'district').prefetch_related(
                'sub_districts').filter(sub_districts__name__contains=self.request.user.sub_district.name)
                                .exclude(delete_request='Yes').distinct())
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

                return queryset_filtered
            return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.RenterFilterForm(self.request.GET)

        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))

        context['filter_form'] = form
        return context


class RenterDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Renter
    context_object_name = 'renter'
    template_name = 'dashboard/people/renter_detail.html'
    permission_model = 'Renter'

    def dispatch(self, request, *args, **kwargs):
        renter = self.get_object()
        user = request.user
        if user.title != 'bs' and renter.delete_request == 'Yes':
            raise PermissionDenied("شما اجازه مشاهده این محتوا را ندارید")
        return super().dispatch(request, *args, **kwargs)


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


# ---------------------------------- Tasks ---------------------------------
class TaskBossURListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_bs_ur_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(status='UR')
            return queryset
        else:
            return models.Task.objects.none()


class TaskBossOPListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_bs_op_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(status='OP')
            return queryset
        else:
            return models.Task.objects.none()


class TaskBossCLListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_bs_cl_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(status='CL')
            return queryset
        else:
            return models.Task.objects.none()


class TaskFPListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_fp_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district')
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset

        elif self.request.user.title == 'fp':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset
        else:
            return models.Task.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TaskFilterForm(self.request.GET)

        context['filter_form'] = form
        return context


class TaskCPListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_cp_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district')
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset

        elif self.request.user.title == 'cp':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset
        else:
            return models.Task.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TaskFilterForm(self.request.GET)

        context['filter_form'] = form
        return context


class TaskBTListView(ReadOnlyPermissionMixin, ListView):
    model = models.Task
    template_name = 'dashboard/tasks/task_bt_list.html'
    context_object_name = 'tasks'
    paginate_by = 6
    permission_model = 'Task'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district')
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset

        elif self.request.user.title == 'bt':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            form = forms.TaskFilterForm(self.request.GET)
            if form.is_valid():
                queryset_filtered = queryset
                if form.cleaned_data['status']:
                    queryset_filtered = queryset_filtered.filter(status=form.cleaned_data['status'])
                queryset_filtered = list(queryset_filtered)
                return queryset_filtered
            return queryset
        else:
            return models.Task.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TaskFilterForm(self.request.GET)

        context['filter_form'] = form
        return context


class TaskDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Task
    context_object_name = 'task'
    template_name = 'dashboard/tasks/task_detail.html'
    permission_model = 'Task'

    def get_queryset(self):
        return models.Task.objects.select_related(
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


class TaskCreateView(PermissionRequiredMixin, CreateView):
    model = models.Task
    form_class = forms.TaskCreateForm
    template_name = 'dashboard/tasks/task_create.html'
    permission_model = 'Task'
    permission_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        deadline = self.request.GET.get('deadline')
        if deadline:
            initial['deadline'] = deadline
        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "وظیفه جدید در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        task_type = self.object.type
        if task_type == 'cp':
            return reverse('task_cp_list')
        elif task_type == 'fp':
            return reverse('task_fp_list')
        elif task_type == 'bt':
            return reverse('task_bt_list')
        return reverse('dashboard')


class TaskUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Task
    form_class = forms.TaskCreateForm
    template_name = 'dashboard/tasks/task_update.html'
    context_object_name = 'task'
    permission_model = 'Task'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        task_type = self.object.type
        if task_type == 'cp':
            return reverse('task_cp_list')
        elif task_type == 'fp':
            return reverse('task_fp_list')
        elif task_type == 'bt':
            return reverse('task_bt_list')
        return reverse('dashboard')


class TaskDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Task
    template_name = 'dashboard/tasks/task_delete.html'
    success_url = reverse_lazy('dashboard')
    context_object_name = 'task'
    permission_model = 'Task'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "وظیفه مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class TaskResultView(PermissionRequiredMixin, UpdateView):
    model = models.Task
    form_class = forms.TaskResultForm
    template_name = 'dashboard/tasks/task_result.html'
    context_object_name = 'task'
    permission_model = 'Task'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (و توسط مدیر مشاهده خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        task_type = self.object.type
        if task_type == 'cp':
            return reverse('task_cp_list')
        elif task_type == 'fp':
            return reverse('task_fp_list')
        elif task_type == 'bt':
            return reverse('task_bt_list')
        return reverse('dashboard')


# -------------------------------- BossTasks -------------------------------
class TaskBossListView(ListView):
    model = models.TaskBoss
    template_name = 'dashboard/boss/boss_task_list.html'
    context_object_name = 'boss_tasks'
    paginate_by = 12

    def get_queryset(self):
        queryset = (models.TaskBoss.objects.select_related('new_sale_file', 'new_rent_file', 'new_buyer', 'new_renter',
                                                           'new_person', 'new_visit', 'new_session', 'ur_task')
                    .filter(condition='op').all())
        form = forms.TaskBossFilterForm(self.request.GET)
        if form.is_valid():
            queryset_filtered = queryset
            if form.cleaned_data['type']:
                queryset_filtered = queryset_filtered.filter(type=form.cleaned_data['type'])
            queryset_filtered = list(queryset_filtered)
            return queryset_filtered
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.TaskBossFilterForm(self.request.GET)

        context['filter_form'] = form
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
        if boss_task.type == 'vs':
            visit = boss_task.new_visit
            form = forms.CombinedVisitStatusForm(visit_instance=visit, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'visit': visit,
            })
        if boss_task.type == 'ss':
            session = boss_task.new_session
            form = forms.CombinedSessionStatusForm(session_instance=session, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'session': session,
            })
        if boss_task.type == 'rv':
            result_visit = boss_task.result_visit
            form = forms.CombinedVisitResultForm(result_visit_instance=result_visit, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'result_visit': result_visit,
            })
        if boss_task.type == 'rs':
            result_session = boss_task.result_session
            form = forms.CombinedSessionResultForm(result_session_instance=result_session, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'result_session': result_session,
            })
        if boss_task.type == 'ts':
            task = boss_task.ur_task
            form = forms.CombinedTaskStatusForm(task_instance=task, boss_instance=boss_task)
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'task': task,
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
        if boss_task.type == 'vs':
            visit = boss_task.new_visit
            form = forms.CombinedVisitStatusForm(request.POST, visit_instance=visit, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'visit': visit,
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
        if boss_task.type == 'rv':
            result_visit = boss_task.result_visit
            form = forms.CombinedVisitResultForm(request.POST, result_visit_instance=result_visit,
                                                 boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'result_visit': result_visit,
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
        if boss_task.type == 'ts':
            task = boss_task.ur_task
            form = forms.CombinedTaskStatusForm(request.POST, task_instance=task, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                messages.success(self.request, "تغییرات در سامانه ثبت شد.")
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'task': task,
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
    sale_files = models.SaleFile.objects.filter(delete_request='Yes')
    rent_files = models.RentFile.objects.filter(delete_request='Yes')
    buyers = models.Buyer.objects.filter(delete_request='Yes')
    renters = models.Renter.objects.filter(delete_request='Yes')
    persons = models.Person.objects.filter(delete_request='Yes')

    for obj in sale_files:
        obj.model_type = 'sale_file'
    for obj in rent_files:
        obj.model_type = 'rent_file'
    for obj in buyers:
        obj.model_type = 'buyer'
    for obj in renters:
        obj.model_type = 'renter'
    for obj in persons:
        obj.model_type = 'person'

    all_objects = list(chain(sale_files, rent_files, buyers, renters, persons))
    try:
        all_objects = sorted(all_objects, key=attrgetter('datetime_created'), reverse=True)
    except AttributeError:
        try:
            all_objects = sorted(all_objects, key=attrgetter('datetime_created'), reverse=True)
        except AttributeError:
            all_objects = sorted(all_objects, key=attrgetter('id'), reverse=True)

    paginator = Paginator(all_objects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    paginated_sale_files = []
    paginated_rent_files = []
    paginated_buyers = []
    paginated_renters = []
    paginated_persons = []

    for obj in page_obj:
        if obj.model_type == 'sale_file':
            paginated_sale_files.append(obj)
        elif obj.model_type == 'rent_file':
            paginated_rent_files.append(obj)
        elif obj.model_type == 'buyer':
            paginated_buyers.append(obj)
        elif obj.model_type == 'renter':
            paginated_renters.append(obj)
        elif obj.model_type == 'person':
            paginated_persons.append(obj)

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


# --------------------------------- Services --------------------------------
class VisitListView(ReadOnlyPermissionMixin, ListView):
    model = models.Visit
    template_name = 'dashboard/services/visit_list.html'
    context_object_name = 'visits'
    paginate_by = 12
    permission_model = 'Visit'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Visit.objects.select_related('agent', 'agent__sub_district').all()
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
                return models.Visit.objects.none()

            user_sub_district = self.request.user.sub_district
            sale_visits = models.Visit.objects.filter(
                sale_file_code__isnull=False,
                sale_file_code__in=models.SaleFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            rent_visits = models.Visit.objects.filter(
                rent_file_code__isnull=False,
                rent_file_code__in=models.RentFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            queryset = (sale_visits | rent_visits).distinct()
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


class VisitCreateView(PermissionRequiredMixin, CreateView):
    model = models.Visit
    form_class = forms.VisitCreateForm
    template_name = 'dashboard/services/visit_create.html'
    permission_model = 'Visit'
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
        messages.success(self.request, "بازدید جدید در سامانه ثبت شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('visit_list')


class VisitUpdateView(PermissionRequiredMixin, UpdateView):
    model = models.Visit
    form_class = forms.VisitCreateForm
    template_name = 'dashboard/services/visit_update.html'
    context_object_name = 'visit'
    permission_model = 'Visit'
    permission_action = 'update'

    def get_queryset(self):
        return models.Visit.objects.select_related(
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
        return reverse('visit_list')


class VisitDeleteView(PermissionRequiredMixin, DeleteView):
    model = models.Visit
    template_name = 'dashboard/services/visit_delete.html'
    success_url = reverse_lazy('visit_list')
    context_object_name = 'visit'
    permission_model = 'Visit'
    permission_action = 'delete'

    def form_valid(self, form):
        messages.error(self.request, "بازدید مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class VisitDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.Visit
    context_object_name = 'visit'
    template_name = 'dashboard/services/visit_detail.html'
    permission_model = 'Visit'

    def get_queryset(self):
        return models.Visit.objects.select_related(
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


class VisitResultView(PermissionRequiredMixin, UpdateView):
    model = models.Visit
    form_class = forms.VisitResultForm
    template_name = 'dashboard/services/visit_result.html'
    context_object_name = 'visit'
    permission_model = 'Visit'
    permission_action = 'update'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (و توسط مدیر مشاهده خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('visit_list')


class SessionListView(ReadOnlyPermissionMixin, ListView):
    model = models.Session
    template_name = 'dashboard/services/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 12
    permission_model = 'Session'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset = models.Session.objects.select_related('agent', 'agent__sub_district').all()
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
    paginate_by = 12
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
                    queryset_filtered = queryset_filtered.filter(followup_code_status=form.cleaned_data['followup_code_status'])
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

    context = {
        'user': user,
        'today': today.strftime('%Y/%m/%d'),
        'month': month,
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

    context = {
        'user': user,
        'today': today.strftime('%Y/%m/%d'),
        'month': month,
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

    context = {
        'user': user,
        'today': today.strftime('%Y/%m/%d'),
        'month': month,
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

    context = {
        'user': user,
        'today': today.strftime('%Y/%m/%d'),
        'month': month,
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

    context = {
        'user': user,
        'today': today.strftime('%Y/%m/%d'),
        'month': month,
        'current_month': current_month,
        'previous_month': previous_month,
        'previous_2_month': previous_2_month,
        'next_month': next_month,
        'next_2_month': next_2_month,
    }

    return render(request, 'dashboard/calendar/2next.html', context=context)


def dated_task_list_view(request):
    user = request.user
    date = request.GET.get('date')
    tasks = models.Task.objects.filter(agent=user)
    if date:
        tasks = models.Task.objects.filter(agent=user).filter(deadline=date)
    context = {
        'user': user,
        'date': date,
        'tasks': tasks,
    }
    print(date)
    return render(request, 'dashboard/tasks/dated_task_list.html', context=context)



