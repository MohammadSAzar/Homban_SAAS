from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.db.models import Prefetch
from django.contrib import messages


from . import models, forms
from .permissions import PermissionRequiredMixin, ReadOnlyPermissionMixin


# ----------------------------------- Bases -----------------------------------
def home_view(request):
    return render(request, 'dashboard/home.html')


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


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
            queryset_default = (models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
                                .filter(sub_district=sub_district))
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

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
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
                form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(district_id=self.request.GET.get('district'))
        context['filter_form'] = form
        return context


class SaleFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'dashboard/files/sale_file_detail.html'
    permission_model = 'SaleFile'


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
                .filter(sub_district=sub_district))
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

                return queryset_filtered
            return queryset_default
        else:
            queryset_default = models.RentFile.objects.select_related('province', 'city', 'district', 'sub_district', 'person')
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
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data['min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data['max_deposit']]
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
                form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(district_id=self.request.GET.get('district'))
        context['filter_form'] = form
        return context


class RentFileDetailView(ReadOnlyPermissionMixin, DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    template_name = 'dashboard/files/rent_file_detail.html'
    permission_model = 'RentFile'


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


# --------------------------------- Persons --------------------------------
class PersonListView(ReadOnlyPermissionMixin, ListView):
    model = models.Person
    template_name = 'dashboard/people/person_list.html'
    context_object_name = 'persons'
    paginate_by = 6
    permission_model = 'Person'

    def get_queryset(self):
        queryset = models.Person.objects.prefetch_related('sale_files', 'rent_files').filter(status='acc').all()
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


# --------------------------------- Buyers --------------------------------
class BuyerListView(ReadOnlyPermissionMixin, ListView):
    model = models.Buyer
    template_name = 'dashboard/people/buyer_list.html'
    context_object_name = 'buyers'
    paginate_by = 6
    permission_model = 'Buyer'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset_default = models.Buyer.objects.select_related('province', 'city', 'district').prefetch_related('sub_districts')

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
                    queryset_filtered = queryset_filtered.filter(sub_districts__in=form.cleaned_data['sub_districts']).distinct()
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
                                         obj.budget_announced and obj.budget_announced >= form.cleaned_data['min_budget']]
                if form.cleaned_data['max_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced <= form.cleaned_data['max_budget']]

                return queryset_filtered
            return queryset_default

        else:
            queryset_default = (models.Buyer.objects.select_related('province', 'city', 'district').prefetch_related('sub_districts')
                                .filter(sub_districts__name__contains=self.request.user.sub_district.name))

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
                    queryset_filtered = queryset_filtered.filter(sub_districts__in=form.cleaned_data['sub_districts']).distinct()
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
                                         obj.budget_announced and obj.budget_announced >= form.cleaned_data['min_budget']]
                if form.cleaned_data['max_budget']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.budget_announced and obj.budget_announced <= form.cleaned_data['max_budget']]

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


# --------------------------------- Renters --------------------------------
class RenterListView(ReadOnlyPermissionMixin, ListView):
    model = models.Renter
    template_name = 'dashboard/people/renter_list.html'
    context_object_name = 'renters'
    paginate_by = 6
    permission_model = 'Renter'

    def get_queryset(self):
        if self.request.user.title == 'bs':
            queryset_default = models.Renter.objects.select_related('province', 'city', 'district').prefetch_related('sub_districts')

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
                    queryset_filtered = queryset_filtered.filter(sub_districts__in=form.cleaned_data['sub_districts']).distinct()
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
                                         obj.deposit_announced and obj.deposit_announced >= form.cleaned_data['min_deposit']]
                if form.cleaned_data['max_deposit']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.deposit_announced and obj.deposit_announced <= form.cleaned_data['max_deposit']]
                if form.cleaned_data['min_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced >= form.cleaned_data['min_rent']]
                if form.cleaned_data['max_rent']:
                    queryset_filtered = [obj for obj in queryset_filtered if
                                         obj.rent_announced and obj.rent_announced <= form.cleaned_data['max_rent']]

                return queryset_filtered
            return queryset_default
        else:
            queryset_default = models.Renter.objects.select_related('province', 'city', 'district').prefetch_related(
                'sub_districts').filter(sub_districts__name__contains=self.request.user.sub_district.name).distinct()
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
            return queryset
        elif self.request.user.title == 'fp':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            return queryset
        else:
            return models.Task.objects.none()


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
            return queryset
        elif self.request.user.title == 'cp':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            return queryset
        else:
            return models.Task.objects.none()


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
            return queryset
        elif self.request.user.title == 'bt':
            agent = self.request.user
            queryset = models.Task.objects.select_related('agent', 'sale_file', 'rent_file', 'buyer', 'renter',
                                                          'agent__sub_district').filter(agent=agent)
            return queryset
        else:
            return models.Task.objects.none()


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
        queryset = models.TaskBoss.objects.select_related('new_sale_file', 'new_rent_file', 'new_buyer', 'new_renter',
                                                          'new_person', 'ur_task').filter(condition='op').all()
        return queryset


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
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'person': person,
            })
        if boss_task.type == 'ts':
            task = boss_task.ur_task
            form = forms.CombinedTaskStatusForm(request.POST, task_instance=task, boss_instance=boss_task)
            if form.is_valid():
                form.save()
                return redirect('boss_task_list')
            return render(request, 'dashboard/boss/boss_task_approve.html', {
                'form': form,
                'boss_task': boss_task,
                'task': task,
            })


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

            return queryset


class VisitCreateView(PermissionRequiredMixin, CreateView):
    model = models.Visit
    form_class = forms.VisitCreateForm
    template_name = 'dashboard/services/visit_create.html'
    permission_model = 'Visit'
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
        self.object = None
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
        self.object = None
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
        self.object = None
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

            return queryset


class SessionCreateView(PermissionRequiredMixin, CreateView):
    model = models.Session
    form_class = forms.SessionCreateForm
    template_name = 'dashboard/services/session_create.html'
    permission_model = 'Session'
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
        self.object = None
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
        self.object = None
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
        self.object = None
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
            return queryset
        else:
            if not self.request.user.sub_district:
                return models.Trade.objects.none()

            user_sub_district = self.request.user.sub_district
            sale_trades = models.Trade.objects.filter(
                sale_file_code__isnull=False,
                sale_file_code__in=models.SaleFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            rent_trades = models.Trade.objects.filter(
                rent_file_code__isnull=False,
                rent_file_code__in=models.RentFile.objects.filter(
                    sub_district=user_sub_district
                ).values_list('code', flat=True)
            )
            queryset = (sale_trades | rent_trades).distinct()
            queryset = queryset.filter(agent=self.request.user)

            return queryset


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
        self.object = None
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
        self.object = None
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
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('trade_list')



