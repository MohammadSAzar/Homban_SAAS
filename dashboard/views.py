from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import login
from django.urls import reverse
from django.views.generic import DetailView, CreateView, ListView
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages

from . import models, forms


# ----------------------------------- Bases -----------------------------------
def home_view(request):
    return render(request, 'dashboard/home.html')


def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')


# --------------------------------- Sale Files ---------------------------------
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
            # queryset_final = queryset_filtered
            if form.cleaned_data['min_price']:
                queryset_filtered = queryset_filtered.filter(price__gte=form.cleaned_data['min_price'])
            if form.cleaned_data['max_price']:
                queryset_filtered = queryset_filtered.filter(price__lte=form.cleaned_data['max_price'])
            if form.cleaned_data['min_area']:
                queryset_filtered = queryset_filtered.filter(area__gte=form.cleaned_data['min_area'])
            if form.cleaned_data['max_area']:
                queryset_filtered = queryset_filtered.filter(area__lte=form.cleaned_data['max_area'])
            if form.cleaned_data['min_room']:
                queryset_filtered = queryset_filtered.filter(room__gte=int(form.cleaned_data['min_room']))
            if form.cleaned_data['max_room']:
                queryset_filtered = queryset_filtered.filter(room__lte=int(form.cleaned_data['max_room']))
            if form.cleaned_data['min_age']:
                queryset_filtered = queryset_filtered.filter(age__gte=int(form.cleaned_data['min_age']))
            if form.cleaned_data['max_age']:
                queryset_filtered = queryset_filtered.filter(age__lte=int(form.cleaned_data['max_age']))
            if form.cleaned_data['min_level']:
                queryset_filtered = queryset_filtered.filter(level__gte=int(form.cleaned_data['min_level']))
            if form.cleaned_data['max_level']:
                queryset_filtered = queryset_filtered.filter(level__lte=int(form.cleaned_data['max_level']))
            return queryset_filtered
        return queryset_default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.SaleFileFilterForm(self.request.GET)

        if self.request.GET.get('province'):
            form.fields['city'].queryset = models.City.objects.filter(province_id=self.request.GET.get('province'))
        if self.request.GET.get('city'):
            form.fields['district'].queryset = models.District.objects.filter(city_id=self.request.GET.get('city'))

        context['filter_form'] = form
        return context


class SaleFileDetailView(DetailView):
    model = models.SaleFile
    context_object_name = 'sale_file'
    template_name = 'restates/sale_file_detail.html'


# class SaleFileCreateView(CreateView):
#     model = models.SaleFile
#     form_class = forms.SaleFileCreateForm
#     template_name = 'restates/sale_file_create.html'
#
#     def post(self, request, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def form_valid(self, form):
#         messages.success(self.request, "آگهی شما پس از تایید ادمین در سایت منتشر خواهد شد.")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         self.object = None
#         return self.render_to_response(self.get_context_data(form=form))
#
#     def get_success_url(self):
#         return reverse('profile_info_now')



