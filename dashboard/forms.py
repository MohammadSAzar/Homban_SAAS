from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils.translation import gettext as _

from . import models, checkers, choices


# --------------------------------- CUM ---------------------------------
class AdminCustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.CustomUserModel
        fields = ('username', 'title',)


class AdminCustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.CustomUserModel
        fields = UserChangeForm.Meta.fields


class LoginForm(forms.ModelForm):
    class Meta:
        model = models.CustomUserModel
        fields = ['username', 'password']


# --------------------------------- Files ---------------------------------
create_sale_file_fields = ['province', 'city', 'district', 'sub_district', 'address', 'price_announced', 'price_min', 'room', 'area',
                           'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'title', 'description', 'source', 'person',
                           'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9', 'video',
                           'direction', 'file_levels', 'apartments_per_level', 'restoration', 'bench_stove', 'balcony',
                           'toilet', 'hot_water', 'cooling', 'heating', 'floor']


sale_file_required_fields = ['province', 'city', 'district', 'sub_district', 'address', 'price_announced', 'price_min', 'room', 'area',
                             'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'title', 'description', 'source', 'person',
                             'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9', 'video',
                             'direction', 'file_levels', 'apartments_per_level', 'restoration', 'bench_stove', 'balcony', 'toilet',
                             'hot_water', 'cooling', 'heating', 'floor']


class SaleFileCreateForm(forms.ModelForm):
    class Meta:
        model = models.SaleFile
        fields = create_sale_file_fields
        widgets = {
            'province': forms.Select(attrs={'id': 'province'}),
            'city': forms.Select(attrs={'id': 'city'}),
            'district': forms.Select(attrs={'id': 'district'}),
            'sub_district': forms.Select(attrs={'id': 'sub_district'})
        }

    def __init__(self, *args, **kwargs):
        super(SaleFileCreateForm, self).__init__(*args, **kwargs)
        for field in sale_file_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        area = cleaned_data.get('area')

        if price and not checkers.file_price_checker(price):
            self.add_error('price', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')
        if area and not checkers.area_checker(area):
            self.add_error('area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        return cleaned_data


class SaleFileFilterForm(forms.Form):
    province = forms.ModelChoiceField(queryset=models.Province.objects.all(), required=False, label=_('Province'))
    city = forms.ModelChoiceField(queryset=models.City.objects.all(), required=False, label=_('City'))
    district = forms.ModelChoiceField(queryset=models.District.objects.all(), required=False, label=_('District'))
    sub_district = forms.ModelChoiceField(queryset=models.SubDistrict.objects.all(), required=False, label=_('Sub-District'))
    min_price = forms.IntegerField(required=False, label=_('Min Price'))
    max_price = forms.IntegerField(required=False, label=_('Max Price'))
    min_area = forms.IntegerField(required=False, label=_('Min Area'))
    max_area = forms.IntegerField(required=False, label=_('Max Area'))
    min_room = forms.ChoiceField(choices=[('', '---------')] + choices.rooms, required=False, label=_('Min Room'))
    max_room = forms.ChoiceField(choices=[('', '---------')] + choices.rooms, required=False, label=_('Max Room'))
    min_age = forms.ChoiceField(choices=[('', '---------')] + choices.ages, required=False, label=_('Min Age'))
    max_age = forms.ChoiceField(choices=[('', '---------')] + choices.ages, required=False, label=_('Max Age'))
    min_level = forms.ChoiceField(choices=[('', '---------')] + choices.levels, required=False, label=_('Min Level'))
    max_level = forms.ChoiceField(choices=[('', '---------')] + choices.levels, required=False, label=_('Max Level'))
    document = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Document'))
    parking = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Parking'))
    elevator = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Elevator'))
    warehouse = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Warehouse'))
    has_images = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Has Images'))
    has_video = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Has Video'))

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        min_area = cleaned_data.get('min_area')
        max_area = cleaned_data.get('max_area')

        if min_price and not checkers.file_price_checker(min_price):
            self.add_error('min_price', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')

        if max_price and not checkers.file_price_checker(max_price):
            self.add_error('max_price', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')

        if min_area and not checkers.area_checker(min_area):
            self.add_error('min_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        if max_area and not checkers.area_checker(max_area):
            self.add_error('max_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        return cleaned_data


