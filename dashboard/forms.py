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
        super(SaleFileCreateForm, self).__init__(*args, **kwargs)
        for field in sale_file_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        price_announced = cleaned_data.get('price_announced')
        price_min = cleaned_data.get('price_min')
        area = cleaned_data.get('area')

        if price_announced and not checkers.file_price_checker(price_announced):
            self.add_error('price_announced', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')
        if price_min and not checkers.file_price_checker(price_min):
            self.add_error('price_min', 'قیمت فایل باید بین 1 تا 1000 میلیارد تومان باشد')
        if area and not checkers.area_checker(area):
            self.add_error('area', 'متراژ فایل باید بین 20 تا 10000 متر باشد.')

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
        phone_number = cleaned_data.get('phone_number')

        if phone_number and not checkers.phone_checker(phone_number):
            self.add_error('phone_number', 'شماره تلفن همراه وارد شده صحیح نیست')

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


# --------------------------------- Tasks ---------------------------------
task_required_fields = ['title', 'type', 'agent', 'deadline', 'description']
task_result_required_fields = ['result', 'status']


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['title', 'type', 'agent', 'deadline', 'sale_file', 'rent_file', 'buyer', 'renter', 'description']

    def __init__(self, *args, **kwargs):
        super(TaskCreateForm, self).__init__(*args, **kwargs)
        self.fields['deadline'] = forms.ChoiceField(
            choices=models.next_month_shamsi(),
            required=True,
            label=self.fields['deadline'].label,
        )
        for field in task_required_fields:
            self.fields[field].required = True


class TaskResultForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ['result', 'status']

    def __init__(self, *args, **kwargs):
        super(TaskResultForm, self).__init__(*args, **kwargs)
        for field in task_result_required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')

        if status != 'UR':
            self.add_error('status', "برای ثبت نتیجه، وضعیت را به 'تحویل داده شده' تغییر دهید.")

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

