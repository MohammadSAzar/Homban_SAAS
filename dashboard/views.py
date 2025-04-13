from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
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
        messages.success(self.request, "فایل شما در سامانه ثبت شد (این فایل توسط مدیر بررسی خواهد شد).")
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

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class SaleFileDeleteView(DeleteView):
    model = models.SaleFile
    template_name = 'dashboard/files/sale_file_delete.html'
    success_url = reverse_lazy('sale_file_list')
    context_object_name = 'sale_file'

    def form_valid(self, form):
        messages.error(self.request, "فایل مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


# --------------------------------- Rent Files --------------------------------
class RentFileListView(ListView):
    model = models.RentFile
    template_name = 'dashboard/files/rent_file_list.html'
    context_object_name = 'rent_files'
    paginate_by = 12

    def get_queryset(self):
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

            # queryset_final = queryset_filtered
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
        form = forms.RentFileFilterForm(self.request.GET)

        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))
        if self.request.GET.get('district'):
            form.fields['sub_district'].queryset = models.SubDistrict.objects.filter(district_id=self.request.GET.get('district'))

        context['filter_form'] = form
        return context


class RentFileDetailView(DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    template_name = 'dashboard/files/rent_file_detail.html'


class RentFileGalleryView(DetailView):
    model = models.RentFile
    context_object_name = 'rent_file'
    template_name = 'dashboard/files/rent_file_gallery.html'


class RentFileCreateView(CreateView):
    model = models.RentFile
    form_class = forms.RentFileCreateForm
    template_name = 'dashboard/files/rent_file_create.html'

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


class RentFileUpdateView(UpdateView):
    model = models.RentFile
    form_class = forms.RentFileCreateForm
    template_name = 'dashboard/files/rent_file_update.html'
    context_object_name = 'rent_file'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


class RentFileDeleteView(DeleteView):
    model = models.RentFile
    template_name = 'dashboard/files/rent_file_delete.html'
    success_url = reverse_lazy('rent_file_list')
    context_object_name = 'rent_file'

    def form_valid(self, form):
        messages.error(self.request, "فایل مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


# --------------------------------- Persons --------------------------------
class PersonListView(ListView):
    model = models.Person
    template_name = 'dashboard/people/person_list.html'
    context_object_name = 'persons'
    paginate_by = 6


class PersonCreateView(CreateView):
    model = models.Person
    form_class = forms.PersonCreateForm
    template_name = 'dashboard/people/person_create.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "فرد آگهی‌دهنده سامانه ثبت شد (این اطلاعات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('person_list')


class PersonUpdateView(UpdateView):
    model = models.Person
    form_class = forms.PersonCreateForm
    template_name = 'dashboard/people/person_update.html'
    context_object_name = 'person'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('person_list')


class PersonDeleteView(DeleteView):
    model = models.Person
    template_name = 'dashboard/people/person_delete.html'
    success_url = reverse_lazy('person_list')
    context_object_name = 'person'

    def form_valid(self, form):
        messages.error(self.request, "فرد مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))


# --------------------------------- Customers --------------------------------
class BuyerListView(ListView):
    model = models.Buyer
    template_name = 'dashboard/people/buyer_list.html'
    context_object_name = 'buyers'
    paginate_by = 6

    def get_queryset(self):
        queryset_default = models.Buyer.objects.select_related('province', 'city', 'district')
        form = forms.BuyerFilterForm(self.request.GET)

        if form.is_valid():
            queryset_filtered = queryset_default
            if form.cleaned_data['province']:
                queryset_filtered = queryset_filtered.filter(province=form.cleaned_data['province'])
            if form.cleaned_data['city']:
                queryset_filtered = queryset_filtered.filter(city=form.cleaned_data['city'])
            if form.cleaned_data['district']:
                queryset_filtered = queryset_filtered.filter(district=form.cleaned_data['district'])
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


class BuyerDetailView(DetailView):
    model = models.Buyer
    context_object_name = 'buyer'
    template_name = 'dashboard/people/buyer_detail.html'


class BuyerCreateView(CreateView):
    model = models.Buyer
    form_class = forms.BuyerCreateForm
    template_name = 'dashboard/people/buyer_create.html'

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


class BuyerUpdateView(UpdateView):
    model = models.Buyer
    form_class = forms.BuyerCreateForm
    template_name = 'dashboard/people/buyer_update.html'
    context_object_name = 'buyer'

    def form_valid(self, form):
        messages.success(self.request, "تغییرات شما در سامانه ثبت شد (این تغییرات توسط مدیر بررسی خواهد شد).")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('buyer_list')


class BuyerDeleteView(DeleteView):
    model = models.Buyer
    template_name = 'dashboard/people/buyer_delete.html'
    success_url = reverse_lazy('buyer_list')
    context_object_name = 'buyer'

    def form_valid(self, form):
        messages.error(self.request, "خریدار مربوطه از سامانه حذف شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = None
        return self.render_to_response(self.get_context_data(form=form))



