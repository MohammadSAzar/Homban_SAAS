from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.utils.translation import gettext as _
from jdatetime import datetime as jdatetime

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


# --------------------------------- Sale Files ---------------------------------
create_sale_file_fields = ['province', 'city', 'district', 'sub_district', 'address', 'price_announced', 'price_min', 'room', 'area',
                           'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'title', 'description', 'source', 'person',
                           'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9', 'video',
                           'direction', 'file_levels', 'apartments_per_level', 'restoration', 'bench_stove', 'balcony',
                           'toilet', 'hot_water', 'cooling', 'heating', 'floor']


sale_file_required_fields = ['province', 'city', 'district', 'sub_district', 'address', 'price_announced', 'room', 'area',
                             'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'title', 'description', 'source',]


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
        self.user = kwargs.pop('user', None)
        super(SaleFileCreateForm, self).__init__(*args, **kwargs)
        for field in sale_file_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        price_announced = cleaned_data.get('price_announced')
        price_min = cleaned_data.get('price_min')
        area = cleaned_data.get('area')
        sub_district = cleaned_data.get('sub_district')

        if price_announced and not checkers.file_price_checker(price_announced):
            self.add_error('price_announced', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')
        if price_min and not checkers.file_price_checker(price_min):
            self.add_error('price_min', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')
        if area and not checkers.area_checker(area):
            self.add_error('area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')
        if self.user.title != 'bs' and sub_district != self.user.sub_district:
            self.add_error('sub_district', 'مشاور اجازه ایجاد فایل جدید در این زیرمحله را ندارد')

        return cleaned_data


class SaleFileFilterForm(forms.Form):
    province = forms.ModelChoiceField(queryset=models.Province.objects.all(), required=False, label=_('Province'))
    city = forms.ModelChoiceField(queryset=models.City.objects.all(), required=False, label=_('City'))
    district = forms.ModelChoiceField(queryset=models.District.objects.all(), required=False, label=_('District'))
    sub_district = forms.ModelChoiceField(queryset=models.SubDistrict.objects.all(), required=False, label=_('Sub-District'))
    person = forms.ModelChoiceField(queryset=models.Person.objects.all(), required=False, label=_('Person'))
    source = forms.ChoiceField(choices=[('', '---------')] + choices.sources, required=False, label=_('Source'))
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
    min_date = forms.CharField(required=False, label='از تاریخ')
    max_date = forms.CharField(required=False, label='تا تاریخ')

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


class SaleFileAgentFilterForm(forms.Form):
    person = forms.ModelChoiceField(queryset=models.Person.objects.all(), required=False, label=_('Person'))
    source = forms.ChoiceField(choices=[('', '---------')] + choices.sources, required=False, label=_('Source'))
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
    min_date = forms.CharField(required=False, label='از تاریخ')
    max_date = forms.CharField(required=False, label='تا تاریخ')

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


class SaleFileDeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.SaleFile
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'Yes':
            self.add_error('delete_request', 'برای درخواست حذف، این فیلد را به "بله" تغییر دهید')
        return cleaned_data


class SaleFileRecoverForm(forms.ModelForm):
    class Meta:
        model = models.SaleFile
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'No':
            self.add_error('delete_request', 'برای بازیابی، این فیلد را به "خیر" تغییر دهید')
        return cleaned_data


# --------------------------------- Files ---------------------------------
create_rent_file_fields = ['province', 'city', 'district', 'sub_district', 'address', 'deposit_announced', 'deposit_min',
                           'rent_announced', 'rent_min', 'convertable', 'room', 'area', 'age', 'document', 'level',
                           'parking', 'elevator', 'warehouse', 'title', 'description', 'source', 'person',
                           'image1', 'image2', 'image3', 'image4', 'image5', 'image6', 'image7', 'image8', 'image9', 'video',
                           'direction', 'file_levels', 'apartments_per_level', 'restoration', 'bench_stove', 'balcony',
                           'toilet', 'hot_water', 'cooling', 'heating', 'floor']


rent_file_required_fields = ['province', 'city', 'district', 'sub_district', 'address', 'deposit_announced', 'rent_announced',
                             'convertable', 'room', 'area', 'age', 'document', 'level', 'parking', 'elevator', 'warehouse', 'title',
                             'description', 'source',]


class RentFileCreateForm(forms.ModelForm):
    class Meta:
        model = models.RentFile
        fields = create_rent_file_fields
        widgets = {
            'province': forms.Select(attrs={'id': 'province'}),
            'city': forms.Select(attrs={'id': 'city'}),
            'district': forms.Select(attrs={'id': 'district'}),
            'sub_district': forms.Select(attrs={'id': 'sub_district'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(RentFileCreateForm, self).__init__(*args, **kwargs)
        for field in rent_file_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        deposit_announced = cleaned_data.get('deposit_announced')
        deposit_min = cleaned_data.get('deposit_min')
        rent_announced = cleaned_data.get('rent_announced')
        rent_min = cleaned_data.get('rent_min')
        area = cleaned_data.get('area')
        sub_district = cleaned_data.get('sub_district')

        if deposit_announced and not checkers.rent_file_deposit_price_checker(deposit_announced):
            self.add_error('deposit_announced', 'مبلغ رهن باید بین صفر تا 100 میلیارد تومان باشد')
        if deposit_min and not checkers.rent_file_deposit_price_checker(deposit_min):
            self.add_error('deposit_min', 'مبلغ رهن باید بین صفر تا 100 میلیارد تومان باشد')
        if rent_announced and not checkers.rent_file_rent_price_checker(rent_announced):
            self.add_error('rent_announced', 'مبلغ اجاره باید بین صفر تا 10 میلیارد تومان باشد')
        if rent_min and not checkers.rent_file_rent_price_checker(rent_min):
            self.add_error('rent_min', 'مبلغ اجاره باید بین صفر تا 10 میلیارد تومان باشد')
        if area and not checkers.area_checker(area):
            self.add_error('area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')
        if self.user.title != 'bs' and sub_district != self.user.sub_district:
            self.add_error('sub_district', 'مشاور اجازه ایجاد فایل جدید در این زیرمحله را ندارد')

        return cleaned_data


class RentFileFilterForm(forms.Form):
    province = forms.ModelChoiceField(queryset=models.Province.objects.all(), required=False, label=_('Province'))
    city = forms.ModelChoiceField(queryset=models.City.objects.all(), required=False, label=_('City'))
    district = forms.ModelChoiceField(queryset=models.District.objects.all(), required=False, label=_('District'))
    sub_district = forms.ModelChoiceField(queryset=models.SubDistrict.objects.all(), required=False, label=_('Sub-District'))
    person = forms.ModelChoiceField(queryset=models.Person.objects.all(), required=False, label=_('Person'))
    source = forms.ChoiceField(choices=[('', '---------')] + choices.sources, required=False, label=_('Source'))
    min_deposit = forms.IntegerField(required=False, label=_('Min Deposit'))
    max_deposit = forms.IntegerField(required=False, label=_('Max Deposit'))
    min_rent = forms.IntegerField(required=False, label=_('Min Rent'))
    max_rent = forms.IntegerField(required=False, label=_('Max Rent'))
    convertable = forms.ChoiceField(choices=[('', '---------')] + choices.beings, required=False, label=_('Convertable'))
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
    min_date = forms.CharField(required=False, label='از تاریخ')
    max_date = forms.CharField(required=False, label='تا تاریخ')

    def clean(self):
        cleaned_data = super().clean()
        min_deposit = cleaned_data.get('min_deposit')
        max_deposit = cleaned_data.get('max_deposit')
        min_rent = cleaned_data.get('min_rent')
        max_rent = cleaned_data.get('max_rent')
        min_area = cleaned_data.get('min_area')
        max_area = cleaned_data.get('max_area')

        if min_deposit and not checkers.rent_file_deposit_price_checker(min_deposit):
            self.add_error('min_deposit', 'مبلغ رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if max_deposit and not checkers.rent_file_deposit_price_checker(max_deposit):
            self.add_error('max_deposit', 'مبلغ رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if min_rent and not checkers.rent_file_rent_price_checker(min_rent):
            self.add_error('min_rent', 'مبلغ اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        if max_rent and not checkers.rent_file_rent_price_checker(max_rent):
            self.add_error('max_rent', 'مبلغ اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        if min_area and not checkers.area_checker(min_area):
            self.add_error('min_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        if max_area and not checkers.area_checker(max_area):
            self.add_error('max_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        return cleaned_data


class RentFileAgentFilterForm(forms.Form):
    person = forms.ModelChoiceField(queryset=models.Person.objects.all(), required=False, label=_('Person'))
    source = forms.ChoiceField(choices=[('', '---------')] + choices.sources, required=False, label=_('Source'))
    min_deposit = forms.IntegerField(required=False, label=_('Min Deposit'))
    max_deposit = forms.IntegerField(required=False, label=_('Max Deposit'))
    min_rent = forms.IntegerField(required=False, label=_('Min Rent'))
    max_rent = forms.IntegerField(required=False, label=_('Max Rent'))
    convertable = forms.ChoiceField(choices=[('', '---------')] + choices.beings, required=False, label=_('Convertable'))
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
    min_date = forms.CharField(required=False, label='از تاریخ')
    max_date = forms.CharField(required=False, label='تا تاریخ')

    def clean(self):
        cleaned_data = super().clean()
        min_deposit = cleaned_data.get('min_deposit')
        max_deposit = cleaned_data.get('max_deposit')
        min_rent = cleaned_data.get('min_rent')
        max_rent = cleaned_data.get('max_rent')
        min_area = cleaned_data.get('min_area')
        max_area = cleaned_data.get('max_area')

        if min_deposit and not checkers.rent_file_deposit_price_checker(min_deposit):
            self.add_error('min_deposit', 'مبلغ رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if max_deposit and not checkers.rent_file_deposit_price_checker(max_deposit):
            self.add_error('max_deposit', 'مبلغ رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if min_rent and not checkers.rent_file_rent_price_checker(min_rent):
            self.add_error('min_rent', 'مبلغ اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        if max_rent and not checkers.rent_file_rent_price_checker(max_rent):
            self.add_error('max_rent', 'مبلغ اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        if min_area and not checkers.area_checker(min_area):
            self.add_error('min_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        if max_area and not checkers.area_checker(max_area):
            self.add_error('max_area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

        return cleaned_data


class RentFileDeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.RentFile
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'Yes':
            self.add_error('delete_request', 'برای درخواست حذف، این فیلد را به "بله" تغییر دهید')
        return cleaned_data


class RentFileRecoverForm(forms.ModelForm):
    class Meta:
        model = models.RentFile
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'No':
            self.add_error('delete_request', 'برای بازیابی فایل، این فیلد را به "خیر" تغییر دهید')
        return cleaned_data


# -------------------------------- People --------------------------------
buyer_required_fields = ['name', 'phone_number', 'description', 'province', 'city', 'district', 'sub_districts',
                         'budget_announced', 'budget_status', 'room_max', 'room_min', 'area_max', 'area_min',
                         'age_max', 'age_min', 'document', 'parking', 'elevator', 'warehouse']

renter_required_fields = ['name', 'phone_number', 'description', 'province', 'city', 'district', 'sub_districts',
                          'deposit_announced', 'rent_announced', 'budget_status', 'convertable', 'room_max', 'room_min',
                          'area_max', 'area_min', 'age_max', 'age_min', 'document', 'parking', 'elevator', 'warehouse']


class PersonCreateForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = ['name', 'phone_number', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone_number = cleaned_data.get('phone_number')

        if phone_number and not checkers.phone_checker(phone_number):
            self.add_error('phone_number', 'شماره تلفن همراه وارد شده صحیح نیست')
        if name and not checkers.name_checker(name):
            self.add_error('name', 'فرمت نام صحیح نیست')

        return cleaned_data


class PersonDeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'Yes':
            self.add_error('delete_request', 'برای درخواست حذف، این فیلد را به "بله" تغییر دهید')
        return cleaned_data


class PersonRecoverForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'No':
            self.add_error('delete_request', 'برای بازیابی فرد آگهی‌دهنده، این فیلد را به "خیر" تغییر دهید')
        return cleaned_data


class BuyerCreateForm(forms.ModelForm):
    sub_districts = forms.ModelMultipleChoiceField(
        queryset=models.SubDistrict.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label='Interested Sub-Districts'
    )

    class Meta:
        model = models.Buyer
        fields = ['name', 'phone_number', 'description', 'province', 'city', 'district', 'sub_districts',
                  'budget_announced', 'budget_max', 'budget_status', 'room_max', 'room_min', 'area_max', 'area_min',
                  'age_max', 'age_min', 'document', 'parking', 'elevator', 'warehouse']
        widgets = {
            'province': forms.Select(attrs={'id': 'province'}),
            'city': forms.Select(attrs={'id': 'city'}),
            'district': forms.Select(attrs={'id': 'district'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in buyer_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        budget_announced = cleaned_data.get('budget_announced')
        budget_max = cleaned_data.get('budget_max')
        area_max = cleaned_data.get('area_max')
        area_min = cleaned_data.get('area_min')
        name = cleaned_data.get('name')

        if phone_number and not checkers.phone_checker(phone_number):
            self.add_error('phone_number', 'شماره تلفن همراه وارد شده صحیح نیست')
        if budget_announced and not checkers.file_price_checker(budget_announced):
            self.add_error('budget_announced', 'بودجه خریدار باید بین 1 تا 1000 میلیارد تومان باشد')
        if budget_max and not checkers.file_price_checker(budget_max):
            self.add_error('budget_max', 'بودجه خریدار باید بین 1 تا 1000 میلیارد تومان باشد')
        if area_max and not checkers.area_checker(area_max):
            self.add_error('area_max', 'متراژ درخواستی خریدار باید بین 20 تا 10000 متر باشد.')
        if area_min and not checkers.area_checker(area_min):
            self.add_error('area_min', 'متراژ درخواستی خریدار باید بین 20 تا 10000 متر باشد.')
        if name and not checkers.name_checker(name):
            self.add_error('name', 'فرمت نام صحیح نیست')

        return cleaned_data


class BuyerFilterForm(forms.Form):
    sub_districts = forms.ModelMultipleChoiceField(
        queryset=models.SubDistrict.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label='Sub-Districts'
    )
    province = forms.ModelChoiceField(queryset=models.Province.objects.all(), required=False, label=_('Province'))
    city = forms.ModelChoiceField(queryset=models.City.objects.all(), required=False, label=_('City'))
    district = forms.ModelChoiceField(queryset=models.District.objects.all(), required=False, label=_('District'))
    min_budget = forms.IntegerField(required=False, label=_('Min Budget'))
    max_budget = forms.IntegerField(required=False, label=_('Max Budget'))
    budget_status = forms.ChoiceField(choices=[('', '---------')] + choices.budgets, required=False, label=_('Budget Status'))
    document = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Document'))
    parking = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Parking'))
    elevator = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Elevator'))
    warehouse = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Warehouse'))

    def clean(self):
        cleaned_data = super().clean()
        min_budget = cleaned_data.get('min_budget')
        max_budget = cleaned_data.get('max_budget')

        if min_budget and not checkers.file_price_checker(min_budget):
            self.add_error('min_budget', 'بودجه مشتری باید بین 1 تا 1000 میلیارد تومان باشد')

        if max_budget and not checkers.file_price_checker(max_budget):
            self.add_error('max_budget', 'بودجه مشتری باید بین 1 تا 1000 میلیارد تومان باشد')

        return cleaned_data


class BuyerDeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.Buyer
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'Yes':
            self.add_error('delete_request', 'برای درخواست حذف، این فیلد را به "بله" تغییر دهید')
        return cleaned_data


class BuyerRecoverForm(forms.ModelForm):
    class Meta:
        model = models.Buyer
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'No':
            self.add_error('delete_request', 'برای بازیابی خریدار، این فیلد را به "خیر" تغییر دهید')
        return cleaned_data


class RenterCreateForm(forms.ModelForm):
    sub_districts = forms.ModelMultipleChoiceField(
        queryset=models.SubDistrict.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label='Interested Sub-Districts'
    )

    class Meta:
        model = models.Renter
        fields = ['name', 'phone_number', 'description', 'province', 'city', 'district', 'sub_districts',
                  'deposit_announced', 'deposit_max', 'rent_announced', 'rent_max', 'budget_status', 'convertable',
                  'room_max', 'room_min', 'area_max', 'area_min', 'age_max', 'age_min', 'document',
                  'parking', 'elevator', 'warehouse']
        widgets = {
            'province': forms.Select(attrs={'id': 'province'}),
            'city': forms.Select(attrs={'id': 'city'}),
            'district': forms.Select(attrs={'id': 'district'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in renter_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        deposit_announced = cleaned_data.get('deposit_announced')
        deposit_max = cleaned_data.get('deposit_max')
        rent_announced = cleaned_data.get('rent_announced')
        rent_max = cleaned_data.get('rent_max')
        area_max = cleaned_data.get('area_max')
        area_min = cleaned_data.get('area_min')
        name = cleaned_data.get('name')

        if phone_number and not checkers.phone_checker(phone_number):
            self.add_error('phone_number', 'شماره تلفن همراه وارد شده صحیح نیست')
        if deposit_announced and not checkers.rent_file_deposit_price_checker(deposit_announced):
            self.add_error('deposit_announced', 'بودجه رهن باید بین 0 تا 100 میلیارد تومان باشد')
        if deposit_max and not checkers.rent_file_deposit_price_checker(deposit_max):
            self.add_error('deposit_max', 'بودجه رهن باید بین 0 تا 100 میلیارد تومان باشد')
        if rent_announced and not checkers.rent_file_rent_price_checker(rent_announced):
            self.add_error('rent_announced', 'بودجه اجاره باید بین 0 تا 10 میلیارد تومان باشد')
        if rent_max and not checkers.rent_file_rent_price_checker(rent_max):
            self.add_error('rent_max', 'بودجه اجاره باید بین 0 تا 10 میلیارد تومان باشد')
        if area_max and not checkers.area_checker(area_max):
            self.add_error('area_max', 'متراژ درخواستی خریدار باید بین 20 تا 10000 متر باشد.')
        if area_min and not checkers.area_checker(area_min):
            self.add_error('area_min', 'متراژ درخواستی خریدار باید بین 20 تا 10000 متر باشد.')
        if name and not checkers.name_checker(name):
            self.add_error('name', 'فرمت نام صحیح نیست')

        return cleaned_data


class RenterFilterForm(forms.Form):
    sub_districts = forms.ModelMultipleChoiceField(
        queryset=models.SubDistrict.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=False,
        label='Sub-Districts'
    )
    province = forms.ModelChoiceField(queryset=models.Province.objects.all(), required=False, label=_('Province'))
    city = forms.ModelChoiceField(queryset=models.City.objects.all(), required=False, label=_('City'))
    district = forms.ModelChoiceField(queryset=models.District.objects.all(), required=False, label=_('District'))
    min_deposit = forms.IntegerField(required=False, label=_('Min Deposit'))
    max_deposit = forms.IntegerField(required=False, label=_('Max Deposit'))
    min_rent = forms.IntegerField(required=False, label=_('Min Rent'))
    max_rent = forms.IntegerField(required=False, label=_('Max Rent'))
    budget_status = forms.ChoiceField(choices=[('', '---------')] + choices.budgets, required=False, label=_('Budget Status'))
    convertable = forms.ChoiceField(choices=[('', '---------')] + choices.beings, required=False, label=_('Convertable'))
    document = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Document'))
    parking = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Parking'))
    elevator = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Elevator'))
    warehouse = forms.ChoiceField(choices=[('', '---------')] + choices.booleans, required=False, label=_('Warehouse'))

    def clean(self):
        cleaned_data = super().clean()
        min_deposit = cleaned_data.get('min_deposit')
        max_deposit = cleaned_data.get('max_deposit')
        min_rent = cleaned_data.get('min_rent')
        max_rent = cleaned_data.get('max_rent')

        if min_deposit and not checkers.rent_file_deposit_price_checker(min_deposit):
            self.add_error('min_deposit', 'بودجه رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if max_deposit and not checkers.rent_file_deposit_price_checker(max_deposit):
            self.add_error('max_deposit', 'بودجه رهن باید بین 0 تا 100 میلیارد تومان باشد')

        if min_rent and not checkers.rent_file_rent_price_checker(min_rent):
            self.add_error('min_rent', 'بودجه اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        if max_rent and not checkers.rent_file_rent_price_checker(max_rent):
            self.add_error('max_rent', 'بودجه اجاره باید بین 0 تا 10 میلیارد تومان باشد')

        return cleaned_data


class RenterDeleteRequestForm(forms.ModelForm):
    class Meta:
        model = models.Renter
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'Yes':
            self.add_error('delete_request', 'برای درخواست حذف، این فیلد را به "بله" تغییر دهید')
        return cleaned_data


class RenterRecoverForm(forms.ModelForm):
    class Meta:
        model = models.Renter
        fields = ['delete_request']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean(self):
        cleaned_data = super().clean()
        delete_request = cleaned_data.get('delete_request')
        if delete_request and delete_request != 'No':
            self.add_error('delete_request', 'برای بازیابی مستاجر، این فیلد را به "خیر" تغییر دهید')
        return cleaned_data


# --------------------------------- Marks ---------------------------------
class MarkCreateForm(forms.ModelForm):
    class Meta:
        model = models.Mark
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


# --------------------------------- Locations ---------------------------------
class ProvinceCreateForm(forms.ModelForm):
    class Meta:
        model = models.Province
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


class CityCreateForm(forms.ModelForm):
    class Meta:
        model = models.City
        fields = ['name', 'province']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


class DistrictCreateForm(forms.ModelForm):
    class Meta:
        model = models.District
        fields = ['name', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


class SubDistrictCreateForm(forms.ModelForm):
    class Meta:
        model = models.SubDistrict
        fields = ['name', 'district', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True


# -------------------------------- Services ---------------------------------
visit_required_fields = ['type', 'date', 'time']
session_required_fields = ['type', 'date', 'time']
trade_required_fields = ['session_code', 'type', 'date', 'contract_owner']


class VisitCreateForm(forms.ModelForm):
    class Meta:
        model = models.Visit
        fields = ['type', 'agent', 'date', 'time', 'sale_file_code', 'rent_file_code', 'buyer_code', 'renter_code',
                  'description']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        sale_file_code = kwargs.pop('sale_file_code', None)
        rent_file_code = kwargs.pop('rent_file_code', None)
        buyer_code = kwargs.pop('buyer_code', None)
        renter_code = kwargs.pop('renter_code', None)
        super(VisitCreateForm, self).__init__(*args, **kwargs)

        self.fields['date'] = forms.ChoiceField(
            choices=models.last_and_next_week_shamsi(),
            required=True,
            label=self.fields['date'].label,
        )

        if sale_file_code:
            self.fields['sale_file_code'].initial = sale_file_code
            self.fields['type'].initial = 'sale'
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از فایل فروش انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل فروش انتخاب شده'
            })
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل فروش انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'sale',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if rent_file_code:
            self.fields['rent_file_code'].initial = rent_file_code
            self.fields['type'].initial = 'rent'
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از فایل اجاره انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل اجاره انتخاب شده'
            })
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل اجاره انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'rent',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if buyer_code:
            self.fields['buyer_code'].initial = buyer_code
            self.fields['type'].initial = 'sale'
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از خریدار انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - خریدار انتخاب شده'
            })
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - خریدار انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'sale',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if renter_code:
            self.fields['renter_code'].initial = renter_code
            self.fields['type'].initial = 'rent'
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از مستاجر انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - مستاجر انتخاب شده'
            })
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - مستاجر انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'rent',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        for field in visit_required_fields:
            self.fields[field].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.title != 'bs':
            instance.agent = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if self.user.title == 'bs':
            agent = cleaned_data.get('agent')
            if agent is None:
                self.add_error('agent', 'انتخاب مشاور برای بازدید الزامی است')
        else:
            agent = self.user
        visit_type = cleaned_data.get('type')
        sale_file_code = cleaned_data.get('sale_file_code')
        rent_file_code = cleaned_data.get('rent_file_code')
        buyer_code = cleaned_data.get('buyer_code')
        renter_code = cleaned_data.get('renter_code')
        is_sale_file_locked = self.fields['sale_file_code'].widget.attrs.get('data-locked') == 'true'
        is_rent_file_locked = self.fields['rent_file_code'].widget.attrs.get('data-locked') == 'true'
        is_buyer_locked = self.fields['buyer_code'].widget.attrs.get('data-locked') == 'true'
        is_renter_locked = self.fields['renter_code'].widget.attrs.get('data-locked') == 'true'

        if is_sale_file_locked:
            if visit_type != 'sale':
                self.add_error('type', 'نوع معامله باید "فروش" باشد - فایل فروش از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['rent_file_code'] = ''
            if renter_code:
                cleaned_data['renter_code'] = ''
        if is_rent_file_locked:
            if visit_type != 'rent':
                self.add_error('type', 'نوع معامله باید "اجاره" باشد - فایل اجاره از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['sale_file_code'] = ''
            if renter_code:
                cleaned_data['buyer_code'] = ''
        if is_buyer_locked:
            if visit_type != 'sale':
                self.add_error('type', 'نوع معامله باید "فروش" باشد - خریدار از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['rent_file_code'] = ''
            if renter_code:
                cleaned_data['renter_code'] = ''
        if is_renter_locked:
            if visit_type != 'rent':
                self.add_error('type', 'نوع معامله باید "اجاره" باشد - مستاجر از قبل انتخاب شده است')
            if sale_file_code:
                cleaned_data['sale_file_code'] = ''
            if buyer_code:
                cleaned_data['buyer_code'] = ''

        sale_file_codes = list(models.SaleFile.objects.values_list('code', flat=True))
        rent_file_codes = list(models.RentFile.objects.values_list('code', flat=True))
        buyer_codes = list(models.Buyer.objects.values_list('code', flat=True))
        renter_codes = list(models.Renter.objects.values_list('code', flat=True))

        if visit_type == 'sale' and not sale_file_code:
            self.add_error('sale_file_code', 'انتخاب فایل فروش الزامی است')
        if visit_type == 'sale' and not buyer_code:
            self.add_error('buyer_code', 'انتخاب مشتری (خریدار) الزامی است')
        if visit_type == 'rent' and not rent_file_code:
            self.add_error('rent_file_code', 'انتخاب فایل اجاره الزامی است')
        if visit_type == 'rent' and not renter_code:
            self.add_error('renter_code', 'انتخاب مشتری (مستاجر) الزامی است')

        if visit_type == 'sale' and rent_file_code:
            self.add_error('rent_file_code', 'نوع معامله فروش است، امکان انتخاب فایل اجاره وجود ندارد')
        if visit_type == 'sale' and renter_code:
            self.add_error('renter_code', 'نوع معامله فروش است، امکان انتخاب مشتری مستاجر وجود ندارد')
        if visit_type == 'rent' and sale_file_code:
            self.add_error('sale_file_code', 'نوع معامله اجاره است، امکان انتخاب فایل فروش وجود ندارد')
        if visit_type == 'rent' and buyer_code:
            self.add_error('buyer_code', 'نوع معامله اجاره است، امکان انتخاب مشتری خریدار وجود ندارد')

        if sale_file_code and sale_file_code not in sale_file_codes:
            self.add_error('sale_file_code', 'کد فایل فروش وارد شده معتبر نیست')
        if rent_file_code and rent_file_code not in rent_file_codes:
            self.add_error('rent_file_code', 'کد فایل اجاره وارد شده معتبر نیست')
        if buyer_code and buyer_code not in buyer_codes:
            self.add_error('buyer_code', 'کد خریدار وارد شده معتبر نیست')
        if renter_code and renter_code not in renter_codes:
            self.add_error('renter_code', 'کد مستاجر وارد شده معتبر نیست')

        if visit_type == 'sale' and sale_file_code in sale_file_codes and buyer_code in buyer_codes:
            sale_file = models.SaleFile.objects.get(code=sale_file_code)
            buyer = models.Buyer.objects.get(code=buyer_code)
            if sale_file.sub_district not in buyer.sub_districts.all():
                self.add_error('sale_file_code', 'فایل فروش و خریدار، زیرمحله مشترک ندارند')
                self.add_error('buyer_code', 'فایل فروش و خریدار، زیرمحله مشترک ندارند')
            if self.user.title:
                if self.user.title == 'fp' or self.user.title == 'bt':
                    if self.user.sub_district != sale_file.sub_district:
                        self.add_error('sale_file_code', 'شما اجازه تنظیم بازدید برای فایل فروش مربوطه را ندارید')
                if self.user.title == 'cp' or self.user.title == 'bt':
                    if self.user.sub_district not in buyer.sub_districts.all():
                        self.add_error('buyer_code', 'شما اجازه تنظیم بازدید برای خریدار مربوطه را ندارید')
            if agent and agent.sub_district != sale_file.sub_district:
                self.add_error('sale_file_code', 'فایل فروش و مشاور، زیرمحله مشترک ندارند')
                self.add_error('agent', 'فایل فروش و مشاور، زیرمحله مشترک ندارند')

        if visit_type == 'rent' and rent_file_code in rent_file_codes and renter_code in renter_codes:
            rent_file = models.RentFile.objects.get(code=rent_file_code)
            renter = models.Renter.objects.get(code=renter_code)
            if rent_file.sub_district not in renter.sub_districts.all():
                self.add_error('rent_file_code', 'فایل اجاره و مستاجر، زیرمحله مشترک ندارند')
                self.add_error('renter_code', 'فایل اجاره و مستاجر، زیرمحله مشترک ندارند')
            if self.user.title == 'fp' or self.user.title == 'bt':
                if self.user.sub_district != rent_file.sub_district:
                    self.add_error('rent_file_code', 'شما اجازه تنظیم بازدید برای فایل اجاره مربوطه را ندارید')
            if self.user.title == 'cp' or self.user.title == 'bt':
                if self.user.sub_district not in renter.sub_districts.all():
                    self.add_error('renter_code', 'شما اجازه تنظیم بازدید برای مستاجر مربوطه را ندارید')
            if agent and agent.sub_district != rent_file.sub_district:
                self.add_error('rent_file_code', 'فایل اجاره و مشاور، زیرمحله مشترک ندارند')
                self.add_error('agent', 'فایل اجاره و مشاور، زیرمحله مشترک ندارند')


class VisitResultForm(forms.ModelForm):
    class Meta:
        model = models.Visit
        fields = ['result', 'status']

    def clean(self):
        cleaned_data = super().clean()
        result = cleaned_data.get('result')
        status = cleaned_data.get('status')

        if result == '':
            self.add_error('result', "در صورت انجام بازدید، ثبت نتیجه آن الزامی است.")
        if status != 'dne':
            self.add_error('status', "برای ثبت نتیجه، تعیین وضعیتی به جز 'انجام شده' مجاز نیست")

        return cleaned_data


class SessionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Session
        fields = ['type', 'agent', 'date', 'time', 'sale_file_code', 'rent_file_code', 'buyer_code', 'renter_code', 'description']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        sale_file_code = kwargs.pop('sale_file_code', None)
        rent_file_code = kwargs.pop('rent_file_code', None)
        buyer_code = kwargs.pop('buyer_code', None)
        renter_code = kwargs.pop('renter_code', None)
        super(SessionCreateForm, self).__init__(*args, **kwargs)

        self.fields['date'] = forms.ChoiceField(
            choices=models.next_week_shamsi(),
            required=True,
            label=self.fields['date'].label,
        )

        if sale_file_code:
            self.fields['sale_file_code'].initial = sale_file_code
            self.fields['type'].initial = 'sale'
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از فایل فروش انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل فروش انتخاب شده'
            })
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل فروش انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'sale',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if rent_file_code:
            self.fields['rent_file_code'].initial = rent_file_code
            self.fields['type'].initial = 'rent'
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از فایل اجاره انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل اجاره انتخاب شده'
            })
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - فایل اجاره انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'rent',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if buyer_code:
            self.fields['buyer_code'].initial = buyer_code
            self.fields['type'].initial = 'sale'
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از خریدار انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - خریدار انتخاب شده'
            })
            self.fields['rent_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - خریدار انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'sale',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        if renter_code:
            self.fields['renter_code'].initial = renter_code
            self.fields['type'].initial = 'rent'
            self.fields['renter_code'].widget.attrs.update({
                'readonly': True,
                'class': 'form-control form-control-xl form-control-outlined bg-light',
                'data-locked': 'true',
                'title': 'این کد از مستاجر انتخاب شده پر شده و قابل تغییر نیست'
            })
            self.fields['buyer_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - مستاجر انتخاب شده'
            })
            self.fields['sale_file_code'].widget.attrs.update({
                'readonly': True,
                'disabled': True,
                'class': 'form-control form-control-xl form-control-outlined bg-secondary text-muted',
                'placeholder': 'غیرفعال - مستاجر انتخاب شده'
            })
            self.fields['type'].widget.attrs.update({
                'data-locked': 'rent',
                'class': 'form-control form-control-xl form-control-outlined'
            })
        for field in session_required_fields:
            self.fields[field].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and self.user.title != 'bs':
            instance.agent = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if self.user.title == 'bs':
            agent = cleaned_data.get('agent')
            if agent is None:
                self.add_error('agent', 'انتخاب مشاور برای نشست الزامی است')
        else:
            agent = self.user
        session_type = cleaned_data.get('type')
        sale_file_code = cleaned_data.get('sale_file_code')
        rent_file_code = cleaned_data.get('rent_file_code')
        buyer_code = cleaned_data.get('buyer_code')
        renter_code = cleaned_data.get('renter_code')
        is_sale_file_locked = self.fields['sale_file_code'].widget.attrs.get('data-locked') == 'true'
        is_rent_file_locked = self.fields['rent_file_code'].widget.attrs.get('data-locked') == 'true'
        is_buyer_locked = self.fields['buyer_code'].widget.attrs.get('data-locked') == 'true'
        is_renter_locked = self.fields['renter_code'].widget.attrs.get('data-locked') == 'true'

        if is_sale_file_locked:
            if session_type != 'sale':
                self.add_error('type', 'نوع معامله باید "فروش" باشد - فایل فروش از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['rent_file_code'] = ''
            if renter_code:
                cleaned_data['renter_code'] = ''
        if is_rent_file_locked:
            if session_type != 'rent':
                self.add_error('type', 'نوع معامله باید "اجاره" باشد - فایل اجاره از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['sale_file_code'] = ''
            if renter_code:
                cleaned_data['buyer_code'] = ''
        if is_buyer_locked:
            if session_type != 'sale':
                self.add_error('type', 'نوع معامله باید "فروش" باشد - خریدار از قبل انتخاب شده است')
            if rent_file_code:
                cleaned_data['rent_file_code'] = ''
            if renter_code:
                cleaned_data['renter_code'] = ''
        if is_renter_locked:
            if session_type != 'rent':
                self.add_error('type', 'نوع معامله باید "اجاره" باشد - مستاجر از قبل انتخاب شده است')
            if sale_file_code:
                cleaned_data['sale_file_code'] = ''
            if buyer_code:
                cleaned_data['buyer_code'] = ''

        sale_file_codes = list(models.SaleFile.objects.values_list('code', flat=True))
        rent_file_codes = list(models.RentFile.objects.values_list('code', flat=True))
        buyer_codes = list(models.Buyer.objects.values_list('code', flat=True))
        renter_codes = list(models.Renter.objects.values_list('code', flat=True))

        if session_type == 'sale' and not sale_file_code:
            self.add_error('sale_file_code', 'انتخاب فایل فروش الزامی است')
        if session_type == 'sale' and not buyer_code:
            self.add_error('buyer_code', 'انتخاب مشتری (خریدار) الزامی است')
        if session_type == 'rent' and not rent_file_code:
            self.add_error('rent_file_code', 'انتخاب فایل اجاره الزامی است')
        if session_type == 'rent' and not renter_code:
            self.add_error('renter_code', 'انتخاب مشتری (مستاجر) الزامی است')

        if session_type == 'sale' and rent_file_code:
            self.add_error('rent_file_code', 'نوع معامله فروش است، امکان انتخاب فایل اجاره وجود ندارد')
        if session_type == 'sale' and renter_code:
            self.add_error('renter_code', 'نوع معامله فروش است، امکان انتخاب مشتری مستاجر وجود ندارد')
        if session_type == 'rent' and sale_file_code:
            self.add_error('sale_file_code', 'نوع معامله اجاره است، امکان انتخاب فایل فروش وجود ندارد')
        if session_type == 'rent' and buyer_code:
            self.add_error('buyer_code', 'نوع معامله اجاره است، امکان انتخاب مشتری خریدار وجود ندارد')

        if sale_file_code and sale_file_code not in sale_file_codes:
            self.add_error('sale_file_code', 'کد فایل فروش وارد شده معتبر نیست')
        if rent_file_code and rent_file_code not in rent_file_codes:
            self.add_error('rent_file_code', 'کد فایل اجاره وارد شده معتبر نیست')
        if buyer_code and buyer_code not in buyer_codes:
            self.add_error('buyer_code', 'کد خریدار وارد شده معتبر نیست')
        if renter_code and renter_code not in renter_codes:
            self.add_error('renter_code', 'کد مستاجر وارد شده معتبر نیست')

        if session_type == 'sale' and sale_file_code in sale_file_codes and buyer_code in buyer_codes:
            sale_file = models.SaleFile.objects.get(code=sale_file_code)
            buyer = models.Buyer.objects.get(code=buyer_code)
            if sale_file.sub_district not in buyer.sub_districts.all():
                self.add_error('sale_file_code', 'فایل فروش و خریدار، زیرمحله مشترک ندارند')
                self.add_error('buyer_code', 'فایل فروش و خریدار، زیرمحله مشترک ندارند')
            if self.user.title:
                if self.user.title == 'fp' or self.user.title == 'bt':
                    if self.user.sub_district != sale_file.sub_district:
                        self.add_error('sale_file_code', 'شما اجازه تنظیم جلسه برای فایل فروش مربوطه را ندارید')
                if self.user.title == 'cp' or self.user.title == 'bt':
                    if self.user.sub_district not in buyer.sub_districts.all():
                        self.add_error('buyer_code', 'شما اجازه تنظیم جلسه برای خریدار مربوطه را ندارید')
            if agent and agent.sub_district != sale_file.sub_district:
                self.add_error('sale_file_code', 'فایل فروش و مشاور، زیرمحله مشترک ندارند')
                self.add_error('agent', 'فایل فروش و مشاور، زیرمحله مشترک ندارند')

        if session_type == 'rent' and rent_file_code in rent_file_codes and renter_code in renter_codes:
            rent_file = models.RentFile.objects.get(code=rent_file_code)
            renter = models.Renter.objects.get(code=renter_code)
            if rent_file.sub_district not in renter.sub_districts.all():
                self.add_error('rent_file_code', 'فایل اجاره و مستاجر، زیرمحله مشترک ندارند')
                self.add_error('renter_code', 'فایل اجاره و مستاجر، زیرمحله مشترک ندارند')
            if self.user.title == 'fp' or self.user.title == 'bt':
                if self.user.sub_district != rent_file.sub_district:
                    self.add_error('rent_file_code', 'شما اجازه تنظیم جلسه برای فایل اجاره مربوطه را ندارید')
            if self.user.title == 'cp' or self.user.title == 'bt':
                if self.user.sub_district not in renter.sub_districts.all():
                    self.add_error('renter_code', 'شما اجازه تنظیم جلسه برای مستاجر مربوطه را ندارید')
            if agent and agent.sub_district != rent_file.sub_district:
                self.add_error('rent_file_code', 'فایل اجاره و مشاور، زیرمحله مشترک ندارند')
                self.add_error('agent', 'فایل اجاره و مشاور، زیرمحله مشترک ندارند')


class SessionResultForm(forms.ModelForm):
    class Meta:
        model = models.Session
        fields = ['result', 'status']

    def clean(self):
        cleaned_data = super().clean()
        result = cleaned_data.get('result')
        status = cleaned_data.get('status')

        if result == '':
            self.add_error('result', "در صورت انجام نشست، ثبت نتیجه آن الزامی است.")
        if status != 'dne':
            self.add_error('status', "برای ثبت نتیجه، تعیین وضعیتی به جز 'انجام شده' مجاز نیست")

        return cleaned_data


class ServiceFilterForm(forms.Form):
    type = forms.ChoiceField(choices=[('', '---------')] + choices.types, required=False, label='نوع')
    status = forms.ChoiceField(choices=[('', '---------')] + choices.serv_statuses, required=False, label='وضعیت')


class TradeCreateForm(forms.ModelForm):
    class Meta:
        model = models.Trade
        fields = ['type', 'session_code', 'date', 'price', 'deposit', 'rent', 'followup_code', 'description',
                  'contract_owner', 'contract_buyer', 'contract_renter']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TradeCreateForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.ChoiceField(
            choices=models.last_month_shamsi(),
            required=True,
            label=self.fields['date'].label,
        )
        for field in trade_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        trade_type = cleaned_data.get('type')
        session_code = cleaned_data.get('session_code')
        price = cleaned_data.get('price')
        deposit = cleaned_data.get('deposit')
        rent = cleaned_data.get('rent')
        contract_owner = cleaned_data.get('contract_owner')
        contract_renter = cleaned_data.get('contract_renter')
        contract_buyer = cleaned_data.get('contract_buyer')

        if contract_owner and not checkers.name_checker(contract_owner):
            self.add_error('contract_owner', 'فرمت نام صحیح نیست')

        session_codes = models.Session.objects.values_list('code', flat=True)
        if session_code in session_codes:
            session = models.Session.objects.get(code=session_code)
            if session.agent != self.user and self.user.title != 'bs':
                self.add_error('session_code', 'شما اجازه ثبت معامله برای این جلسه را ندارید')
            if trade_type != session.type:
                self.add_error('session_code', 'نوع جلسه انتخابی با نوع معامله متفاوت است')
        if session_code and session_code not in session_codes:
            self.add_error('session_code', 'کد جلسه وارد شده، معتبر نیست')

        if trade_type == 'sale':
            if deposit:
                self.add_error('deposit', 'برای معامله فروش، امکان تعیین مبلغ ودیعه (رهن) وجود ندارد')
            if rent:
                self.add_error('rent', 'برای معامله فروش، امکان تعیین مبلغ اجاره وجود ندارد')
            if contract_renter:
                self.add_error('contract_renter', 'برای معامله فروش، امکان تعیین نام مستاجر وجود ندارد')
            if not contract_buyer:
                self.add_error('contract_buyer', 'تعیین نام خریدار (طبق قرارداد) الزامی است')
            if contract_buyer and not checkers.name_checker(contract_buyer):
                self.add_error('contract_buyer', 'فرمت نام صحیح نیست')
        if trade_type == 'rent':
            if price:
                self.add_error('price', 'برای معامله اجاره، فقط باید ودیعه و اجاره تعیین گردد')
            if contract_buyer:
                self.add_error('contract_buyer', 'برای معامله اجاره، امکان تعیین نام خریدار وجود ندارد')
            if not contract_renter:
                self.add_error('contract_renter', 'تعیین نام مستاجر (طبق قرارداد) الزامی است')
            if contract_renter and not checkers.name_checker(contract_renter):
                self.add_error('contract_renter', 'فرمت نام صحیح نیست')

        if price and not checkers.file_price_checker(price):
            self.add_error('price', 'قیمت معامله باید بین 1 تا 1000 میلیارد تومان باشد')
        if deposit and not checkers.rent_file_deposit_price_checker(deposit):
            self.add_error('deposit', 'مبلغ ودیعه (رهن) باید بین صفر تا 100 میلیارد تومان باشد')
        if rent and not checkers.rent_file_rent_price_checker(rent):
            self.add_error('rent', 'مبلغ اجاره باید بین صفر تا 10 میلیارد تومان باشد')


class TradeCodeForm(forms.ModelForm):
    class Meta:
        model = models.Trade
        fields = ['followup_code']

    def clean(self):
        cleaned_data = super().clean()
        followup_code = cleaned_data.get('followup_code')

        # if followup_code != '':
        #     if followup_code != 'end':
        #         self.add_error('status', "برای ثبت نتیجه، وضعیت را به 'خاتمه یافته' تغییر دهید.")

        return cleaned_data


class TradeFilterForm(forms.Form):
    type = forms.ChoiceField(choices=[('', '---------')] + choices.types, required=False, label='نوع')
    followup_code_status = forms.ChoiceField(choices=[('', '---------')] + choices.fc_statuses, required=False, label='کد رهگیری')


# ---------------------------------- Tasks ----------------------------------
task_required_fields = ['title', 'type', 'agent', 'deadline', 'description']


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['title', 'type', 'agent', 'deadline', 'sale_file_code', 'rent_file_code', 'buyer_code', 'renter_code', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        initial_deadline = self.initial.get('deadline') or self.data.get('deadline')
        if 'deadline' in self.initial or 'deadline' in self.data:
            self.fields['deadline'] = forms.CharField(
                initial=initial_deadline,
                required=True,
                label='مهلت انجام',
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )
        else:
            self.fields['deadline'] = forms.ChoiceField(
                choices=models.next_month_shamsi(),
                required=True,
                label='مهلت انجام'
            )
        if self.request and self.request.user.title != 'bs':
            self.fields['agent'].initial = self.request.user

            class ReadOnlyUserWidget(forms.TextInput):
                def __init__(self, user, *args, **kwargs):
                    self.user = user
                    super().__init__(*args, **kwargs)
                    self.attrs.update({'readonly': 'readonly'})

                def format_value(self, value):
                    return self.user.username

                def value_from_datadict(self, data, files, name):
                    return self.user.pk

            self.fields['agent'].widget = ReadOnlyUserWidget(self.request.user)
        else:
            self.fields['agent'].queryset = models.CustomUserModel.objects.exclude(title='bs')
        for field in task_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        task_type = cleaned_data.get('type')
        agent = cleaned_data.get('agent')
        sale_file_code = cleaned_data.get('sale_file_code')
        rent_file_code = cleaned_data.get('rent_file_code')
        buyer_code = cleaned_data.get('buyer_code')
        renter_code = cleaned_data.get('renter_code')
        deadline = cleaned_data.get('deadline')

        if deadline:
            try:
                year, month, day = map(int, deadline.split('/'))
                deadline_date = jdatetime(year, month, day)
                today = jdatetime.now().date()
                if deadline_date < today:
                    self.add_error('deadline', 'ددلاین انتخابی گذشته است')
            except (ValueError, AttributeError):
                self.add_error('deadline', 'فرمت تاریخ نامعتبر است')

        sale_file_codes = list(models.SaleFile.objects.values_list('code', flat=True))
        rent_file_codes = list(models.RentFile.objects.values_list('code', flat=True))
        buyer_codes = list(models.Buyer.objects.values_list('code', flat=True))
        renter_codes = list(models.Renter.objects.values_list('code', flat=True))

        if sale_file_code and sale_file_code not in sale_file_codes:
            self.add_error('sale_file_code', 'کد فایل فروش وارد شده معتبر نیست')
        if rent_file_code and rent_file_code not in rent_file_codes:
            self.add_error('rent_file_code', 'کد فایل اجاره وارد شده معتبر نیست')
        if buyer_code and buyer_code not in buyer_codes:
            self.add_error('buyer_code', 'کد خریدار وارد شده معتبر نیست')
        if renter_code and renter_code not in renter_codes:
            self.add_error('renter_code', 'کد مستاجر وارد شده معتبر نیست')

        if sale_file_code and sale_file_code in sale_file_codes:
            sale_file = models.SaleFile.objects.get(code=sale_file_code)
            if sale_file.sub_district != agent.sub_district:
                self.add_error('sale_file_code', 'فایل فروش و مشاور مربوطه، زیرمحله مشترک ندارند')
        if rent_file_code and rent_file_code in rent_file_codes:
            rent_file = models.RentFile.objects.get(code=rent_file_code)
            if rent_file.sub_district != agent.sub_district:
                self.add_error('rent_file_code', 'فایل اجاره و مشاور مربوطه، زیرمحله مشترک ندارند')
        if buyer_code and buyer_code in buyer_codes:
            buyer = models.Buyer.objects.get(code=buyer_code)
            if agent.sub_district not in buyer.sub_districts.all():
                self.add_error('buyer_code', 'خریدار و مشاور مربوطه، زیرمحله مشترک ندارند')
        if renter_code and renter_code in renter_codes:
            renter = models.Renter.objects.get(code=renter_code)
            if agent.sub_district not in renter.sub_districts.all():
                self.add_error('renter_code', 'مستاجر و مشاور مربوطه، زیرمحله مشترک ندارند')

        if agent and agent.title == 'bs':
            self.add_error('agent', 'امکان تعریف وظیفه برای مدیر وجود ندارد')
        if agent and agent.title != task_type and agent.title != 'bs':
            self.add_error('agent', 'مشاور انتخابی با "نوع وظیفه" همخوانی ندارد')
            self.add_error('type', 'نوع وظیفه با "مشاور انتخابی" همخوانی ندارد')

        return cleaned_data


class TaskResultForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['result', 'status']

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        result = cleaned_data.get('result')

        if result != '':
            if status != 'UR':
                self.add_error('status', "برای ثبت نتیجه، وضعیت را به 'تحویل داده شده' تغییر دهید.")
        if status == 'CL':
            self.add_error('status', "بستن وظیفه فقط از طریق پنل مدیر ممکن است.")

        return cleaned_data


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TaskAdminForm, self).__init__(*args, **kwargs)

        self.fields['deadline'] = forms.ChoiceField(
            choices=models.next_month_shamsi(),
            required=False,
            label=self.fields['deadline'].label,
        )


class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', '---------')] + choices.task_statuses, required=False, label='وضعیت وظیفه')


# -------------------------------- BossTasks --------------------------------
class TaskBossFilterForm(forms.Form):
    type = forms.ChoiceField(choices=[('', '---------')] + choices.boss_task_types, required=False, label='وضعیت وظیفه')


class TaskBossStatusForm(forms.ModelForm):
    class Meta:
        model = models.TaskBoss
        fields = ['condition']

    def clean(self):
        condition = self.cleaned_data.get('condition')
        if not condition:
            self.add_error('condition', 'این فیلد لازم است')


class SaleFileStatusForm(forms.ModelForm):
    class Meta:
        model = models.SaleFile
        fields = ['status']


class RentFileStatusForm(forms.ModelForm):
    class Meta:
        model = models.RentFile
        fields = ['status']


class BuyerStatusForm(forms.ModelForm):
    class Meta:
        model = models.Buyer
        fields = ['status']


class RenterStatusForm(forms.ModelForm):
    class Meta:
        model = models.Renter
        fields = ['status']


class PersonStatusForm(forms.ModelForm):
    class Meta:
        model = models.Person
        fields = ['status']


class VisitStatusForm(forms.ModelForm):
    class Meta:
        model = models.Visit
        fields = ['status', 'boss_notes']


class SessionStatusForm(forms.ModelForm):
    class Meta:
        model = models.Session
        fields = ['status', 'boss_notes']


class VisitResultBossForm(forms.ModelForm):
    class Meta:
        model = models.Visit
        fields = ['status', 'boss_final_comment']


class SessionResultBossForm(forms.ModelForm):
    class Meta:
        model = models.Session
        fields = ['status', 'boss_final_comment']


class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['status']


class CombinedTaskStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.task_instance = kwargs.pop('task_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.task_form = TaskStatusForm(data=data, instance=self.task_instance)

    def is_valid(self):
        valid = self.task_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        condition = self.boss_form.cleaned_data.get('condition')
        status = self.task_form.cleaned_data.get('status')

        if status == 'OP' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "باز"، این فیلد باید "بسته" باشد')
            self.task_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "تحویل داده شده" باشد')
            return False
        if status == 'UR' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "تحویل داده شده"،این فیلد باید "باز" باشد')
            self.task_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "باز" یا "بسته" باشد')
            return False
        if status == 'UR' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.task_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False
        if status == 'CL' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "بسته"، این فیلد باید "بسته" باشد')
            self.task_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "تحویل داده شده" باشد')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.task_form.save()


class CombinedSaleFileStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.sale_file_instance = kwargs.pop('sale_file_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.sale_file_form = SaleFileStatusForm(data=data, instance=self.sale_file_instance)

    def is_valid(self):
        valid = self.sale_file_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.sale_file_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "پذیرفته شده"، این فیلد باید "بسته" باشد')
            self.sale_file_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"،این فیلد باید "بسته" باشد')
            self.sale_file_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'pen' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "در انتظار"،این فیلد باید "باز" باشد')
            self.sale_file_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "رد شده" یا "پذیرفته ‌شده" باشد')
            return False
        if status == 'pen' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.sale_file_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.sale_file_form.save()


class CombinedRentFileStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.rent_file_instance = kwargs.pop('rent_file_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.rent_file_form = RentFileStatusForm(data=data, instance=self.rent_file_instance)

    def is_valid(self):
        valid = self.rent_file_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.rent_file_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "پذیرفته شده"، این فیلد باید "بسته" باشد')
            self.rent_file_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"،این فیلد باید "بسته" باشد')
            self.rent_file_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'pen' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "در انتظار"،این فیلد باید "باز" باشد')
            self.rent_file_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "رد شده" یا "پذیرفته ‌شده" باشد')
            return False
        if status == 'pen' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.rent_file_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.rent_file_form.save()


class CombinedBuyerStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.buyer_instance = kwargs.pop('buyer_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.buyer_form = BuyerStatusForm(data=data, instance=self.buyer_instance)

    def is_valid(self):
        valid = self.buyer_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.buyer_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "پذیرفته شده"، این فیلد باید "بسته" باشد')
            self.buyer_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"،این فیلد باید "بسته" باشد')
            self.buyer_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'pen' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "در انتظار"،این فیلد باید "باز" باشد')
            self.buyer_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "رد شده" یا "پذیرفته ‌شده" باشد')
            return False
        if status == 'pen' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.buyer_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.buyer_form.save()


class CombinedRenterStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.renter_instance = kwargs.pop('renter_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.renter_form = RenterStatusForm(data=data, instance=self.renter_instance)

    def is_valid(self):
        valid = self.renter_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.renter_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "پذیرفته شده"، این فیلد باید "بسته" باشد')
            self.renter_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"،این فیلد باید "بسته" باشد')
            self.renter_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'pen' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "در انتظار"،این فیلد باید "باز" باشد')
            self.renter_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "رد شده" یا "پذیرفته ‌شده" باشد')
            return False
        if status == 'pen' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.renter_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.renter_form.save()


class CombinedPersonStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.person_instance = kwargs.pop('person_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.person_form = PersonStatusForm(data=data, instance=self.person_instance)

    def is_valid(self):
        valid = self.person_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.person_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "پذیرفته شده"، این فیلد باید "بسته" باشد')
            self.person_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"،این فیلد باید "بسته" باشد')
            self.person_form.add_error('status', 'برای وظیفه مدیریتی "باز"، این فیلد باید "در انتظار" باشد')
            return False
        if status == 'pen' and condition == 'cl':
            self.boss_form.add_error('condition', 'برای وضعیت "در انتظار"،این فیلد باید "باز" باشد')
            self.person_form.add_error('status', 'برای وظیفه مدیریتی "بسته"، این فیلد باید "رد شده" یا "پذیرفته ‌شده" باشد')
            return False
        if status == 'pen' and condition == 'op':
            self.boss_form.add_error('condition', 'هیچ تغییری در فرم ایجاد نشده است')
            self.person_form.add_error('status', 'هیچ تغییری در فرم ایجاد نشده است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.person_form.save()


class CombinedVisitStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.visit_instance = kwargs.pop('visit_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.visit_form = VisitStatusForm(data=data, instance=self.visit_instance)

    def is_valid(self):
        valid = self.visit_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.visit_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'sub' and condition == 'op':
            self.visit_form.add_error('status', 'هیچ تغییری اعمال نشده است')
            self.boss_form.add_error('condition', 'هیچ تغییری اعمال نشده است')
            return False
        if status == 'sub' and condition == 'cl':
            self.visit_form.add_error('status', 'برای بستن وظیفه مدیریتی، این فیلد باید "تایید شده" یا "رد شده" باشد')
            return False
        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "تایید شده"، این فیلد باید "بسته" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"، این فیلد باید "بسته" باشد')
            return False
        if status == 'dne' or status == 'end':
            self.visit_form.add_error('status', 'انتخاب "انجام شده" و "تایید نتیجه" برای این فیلد، فعلا مجاز نیست')
            return False
        if not condition:
            self.boss_form.add_error('condition', 'تعیین این فیلد الزامی است')
            return False
        if not status:
            self.visit_form.add_error('status', 'تعیین این فیلد الزامی است')
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.visit_form.save()


class CombinedSessionStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.session_instance = kwargs.pop('session_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.session_form = SessionStatusForm(data=data, instance=self.session_instance)

    def is_valid(self):
        valid = self.session_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.session_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status == 'sub' and condition == 'op':
            self.session_form.add_error('status', 'هیچ تغییری اعمال نشده است')
            self.boss_form.add_error('condition', 'هیچ تغییری اعمال نشده است')
            return False
        if status == 'sub' and condition == 'cl':
            self.session_form.add_error('status', 'برای بستن وظیفه مدیریتی، این فیلد باید "تایید شده" یا "رد شده" باشد')
            return False
        if status == 'acc' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "تایید شده"، این فیلد باید "بسته" باشد')
            return False
        if status == 'can' and condition == 'op':
            self.boss_form.add_error('condition', 'برای وضعیت "رد شده"، این فیلد باید "بسته" باشد')
            return False
        if status == 'dne' or status == 'end':
            self.session_form.add_error('status', 'انتخاب "انجام شده" و "تایید نتیجه" برای این فیلد، فعلا مجاز نیست')
            return False
        if not condition:
            self.boss_form.add_error('condition', 'تعیین این فیلد الزامی است')
            return False
        if not status:
            self.session_form.add_error('status', 'تعیین این فیلد الزامی است')
            return False
        return True

    def save(self):
        self.boss_form.save()
        self.session_form.save()


class CombinedVisitResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.result_visit_instance = kwargs.pop('result_visit_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.result_visit_form = VisitResultBossForm(data=data, instance=self.result_visit_instance)

    def is_valid(self):
        valid = self.result_visit_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.result_visit_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status != 'end':
            self.result_visit_form.add_error('status', "برای بازدید انجام شده، این فیلد فقط می‌تواند 'تایید نتیجه' باشد")
            return False
        if condition != 'cl':
            self.boss_form.add_error('condition', "برای تایید نتیجه، این فیلد باید 'بسته' باشد")
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.result_visit_form.save()


class CombinedSessionResultForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.boss_instance = kwargs.pop('boss_instance', None)
        self.result_session_instance = kwargs.pop('result_session_instance', None)
        super().__init__(*args, **kwargs)

        data = args[0] if args else None
        self.boss_form = TaskBossStatusForm(data=data, instance=self.boss_instance)
        self.result_session_form = SessionResultBossForm(data=data, instance=self.result_session_instance)

    def is_valid(self):
        valid = self.result_session_form.is_valid() and self.boss_form.is_valid()
        return valid and self._cross_form_validation()

    def _cross_form_validation(self):
        status = self.result_session_form.cleaned_data.get('status')
        condition = self.boss_form.cleaned_data.get('condition')

        if status != 'end':
            self.result_session_form.add_error('status', "برای نشست انجام شده، این فیلد فقط می‌تواند 'تایید نتیجه' باشد")
            return False
        if condition != 'cl':
            self.boss_form.add_error('condition', "برای تایید نتیجه، این فیلد باید 'بسته' باشد")
            return False

        return True

    def save(self):
        self.boss_form.save()
        self.result_session_form.save()


