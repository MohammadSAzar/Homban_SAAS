from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, CreateView, ListView, UpdateView
from django.contrib import messages

from . import models, forms


# ----------------------------------- Bases -----------------------------------
def home_view(request):
    return render(request, 'dashboard/home.html')


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


# --------------------------------- Sale Files --------------------------------
class SaleFileListView(ListView):
    model = models.SaleFile
    template_name = 'dashboard/files/sale_file_list.html'
    context_object_name = 'sale_files'
    paginate_by = 12

    def get_queryset(self):
        queryset_default = models.SaleFile.objects.select_related('province', 'city', 'district', 'sub_district')
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

            # queryset_final = queryset_filtered
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
        form = forms.SaleFileFilterForm(self.request.GET)

        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
        if self.request.GET.get('district'):
            form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(district_id=self.request.GET.get('district'))

        context['filter_form'] = form
        return context


class SaleFileDetailView(DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'dashboard/files/sale_file_detail.html'


class SaleFileGalleryView(DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'dashboard/files/sale_file_gallery.html'


class SaleFileCreateView(CreateView):
    model = models.SaleFile
    form_class = forms.SaleFileCreateForm
    template_name = 'dashboard/files/sale_file_create.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "فایل شما پس از تایید مدیر در سایت منتشر خواهد شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('sale_file_list')


class SaleFileUpdateView(UpdateView):
    model = models.SaleFile
    form_class = forms.SaleFileCreateForm
    template_name = 'dashboard/files/sale_file_update.html'
    context_object_name = 'sale_file'


