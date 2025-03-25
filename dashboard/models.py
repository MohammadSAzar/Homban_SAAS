import random
import string
from jdatetime import date, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext as _

from . import choices


# -------------------------------- CODES --------------------------------
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_unique_code():
    return ''.join(random.choices(string.digits + string.digits, k=6))


# -------------------------------- TIMES --------------------------------
def next_seven_days_shamsi():
    days = []
    today = date.today()
    for i in range(1, 8):
        next_day = today + timedelta(days=i)
        days.append({
            'result_day': next_day.strftime('%A'),
            'result_date': next_day.strftime('%Y/%m/%d')
        })
    for j in range(0, 7):
        if days[j]['result_day'] == 'Monday' or days[j]['result_day'] == 'monday':
            days[j]['result_day'] = 'دوشنبه'
        if days[j]['result_day'] == 'Tuesday' or days[j]['result_day'] == 'tuesday':
            days[j]['result_day'] = 'سه‌شنبه'
        if days[j]['result_day'] == 'Wednesday' or days[j]['result_day'] == 'wednesday':
            days[j]['result_day'] = 'چهارشنبه'
        if days[j]['result_day'] == 'Thursday' or days[j]['result_day'] == 'thursday':
            days[j]['result_day'] = 'پنج‌شنبه'
        if days[j]['result_day'] == 'Friday' or days[j]['result_day'] == 'friday':
            days[j]['result_day'] = 'جمعه'
        if days[j]['result_day'] == 'Saturday' or days[j]['result_day'] == 'saturday':
            days[j]['result_day'] = 'شنبه'
        if days[j]['result_day'] == 'Sunday' or days[j]['result_day'] == 'sunday':
            days[j]['result_day'] = 'یکشنبه'
    final_days = []
    for k in range(0, 7):
        converted_day = str(days[k]['result_day'] + ' - ' + days[k]['result_date'])
        final_days.append((
            'result_day', converted_day,
        ))
    return final_days


def last_month_shamsi():
    days = []
    today = date.today()
    for i in range(1, 31):
        previous_day = today - timedelta(days=i)
        days.append({
            'result_day': previous_day.strftime('%A'),
            'result_date': previous_day.strftime('%Y/%m/%d')
        })
    for j in range(0, 30):
        if days[j]['result_day'] == 'Monday' or days[j]['result_day'] == 'monday':
            days[j]['result_day'] = 'دوشنبه'
        if days[j]['result_day'] == 'Tuesday' or days[j]['result_day'] == 'tuesday':
            days[j]['result_day'] = 'سه‌شنبه'
        if days[j]['result_day'] == 'Wednesday' or days[j]['result_day'] == 'wednesday':
            days[j]['result_day'] = 'چهارشنبه'
        if days[j]['result_day'] == 'Thursday' or days[j]['result_day'] == 'thursday':
            days[j]['result_day'] = 'پنج‌شنبه'
        if days[j]['result_day'] == 'Friday' or days[j]['result_day'] == 'friday':
            days[j]['result_day'] = 'جمعه'
        if days[j]['result_day'] == 'Saturday' or days[j]['result_day'] == 'saturday':
            days[j]['result_day'] = 'شنبه'
        if days[j]['result_day'] == 'Sunday' or days[j]['result_day'] == 'sunday':
            days[j]['result_day'] = 'یکشنبه'
    final_days = []
    for k in range(0, 30):
        converted_day = str(days[k]['result_day'] + ' - ' + days[k]['result_date'])
        final_days.append((
            'result_day', converted_day,
        ))
    return final_days


def next_month_shamsi():
    days = []
    today = date.today()
    for i in range(1, 31):
        next_day = today + timedelta(days=i)
        days.append({
            'result_day': next_day.strftime('%A'),
            'result_date': next_day.strftime('%Y/%m/%d')
        })
    for j in range(0, 30):
        if days[j]['result_day'] == 'Monday' or days[j]['result_day'] == 'monday':
            days[j]['result_day'] = 'دوشنبه'
        if days[j]['result_day'] == 'Tuesday' or days[j]['result_day'] == 'tuesday':
            days[j]['result_day'] = 'سه‌شنبه'
        if days[j]['result_day'] == 'Wednesday' or days[j]['result_day'] == 'wednesday':
            days[j]['result_day'] = 'چهارشنبه'
        if days[j]['result_day'] == 'Thursday' or days[j]['result_day'] == 'thursday':
            days[j]['result_day'] = 'پنج‌شنبه'
        if days[j]['result_day'] == 'Friday' or days[j]['result_day'] == 'friday':
            days[j]['result_day'] = 'جمعه'
        if days[j]['result_day'] == 'Saturday' or days[j]['result_day'] == 'saturday':
            days[j]['result_day'] = 'شنبه'
        if days[j]['result_day'] == 'Sunday' or days[j]['result_day'] == 'sunday':
            days[j]['result_day'] = 'یکشنبه'
    final_days = []
    for k in range(0, 30):
        converted_day = str(days[k]['result_day'] + ' - ' + days[k]['result_date'])
        final_days.append((
            'result_day', converted_day,
        ))
    return final_days


# --------------------------------- CUM -----------------------------------
class CustomUserModel(AbstractUser):
    TITLE_CHOICES = [
        ('fp', _('File Person')),
        ('cp', _('Customer Person')),
        ('cr', _('Coordinator')),
        ('bs', _('Boss')),
    ]
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, null=True, verbose_name=_('Title'))
    email = models.EmailField(unique=False, blank=True, null=True)
    REQUIRED_FIELDS = []


# --------------------------------- LOCs ----------------------------------
class Province(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Province'))

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('City'))
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100, default='_', verbose_name=_('District Name'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return self.name


class SubDistrict(models.Model):
    name = models.CharField(max_length=100, default='_', verbose_name=_('Sub-District Name'))
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sub_districts')

    def __str__(self):
        return self.name


# --------------------------------- FILE ---------------------------------
class Person(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))

    def __str__(self):
        return self.name


class SaleFile(models.Model):
    # location fields
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files', verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files', verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files', verbose_name=_('District'))
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files', verbose_name=_('Sub-District'))
    address = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Address'))
    # general characteristics
    price_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Price'))
    price_min = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Min Price'))
    room = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Number of Rooms'))
    area = models.PositiveIntegerField(verbose_name=_('Area'))
    age = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Age of Apartment'))
    document = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Document'))
    level = models.CharField(max_length=15, choices=choices.levels, verbose_name=_('Level'))
    parking = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Parking'))
    elevator = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Elevator'))
    warehouse = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Warehouse'))
    # media
    image1 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 1'))
    image2 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 2'))
    image3 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 3'))
    image4 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 4'))
    image5 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 5'))
    image6 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 6'))
    image7 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 7'))
    image8 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 8'))
    image9 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 9'))
    video = models.FileField(upload_to='videos/', null=True, blank=True, verbose_name=_('Video'))
    has_image = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, default='hasnt', verbose_name=_('Has Image?'))
    has_video = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, default='hasnt', verbose_name=_('Has Video?'))
    # optional
    direction = models.CharField(max_length=15, choices=choices.directions, null=True, blank=True, verbose_name=_('Direction'))
    file_levels = models.CharField(max_length=15, choices=choices.levels, null=True, blank=True, verbose_name=_('Levels Number'))
    apartments_per_level = models.CharField(max_length=15, choices=choices.apartments_per_level, null=True, blank=True, verbose_name=_('Apartments per Level'))
    restoration = models.CharField(max_length=15, choices=choices.restorations, null=True, blank=True, verbose_name=_('Restoration'))
    bench_stove = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, verbose_name=_('Bench Stove'))
    balcony = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, verbose_name=_('Balcony'))
    toilet = models.CharField(max_length=15, choices=choices.toilets, null=True, blank=True, verbose_name=_('Toilet'))
    hot_water = models.CharField(max_length=15, choices=choices.hot_water, null=True, blank=True, verbose_name=_('Hot Water System'))
    cooling = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Cooling System'))
    heating = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Heating System'))
    floor = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Floor Type'))
    # general information
    title = models.CharField(max_length=230, verbose_name=_('Title'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    source = models.CharField(max_length=15, choices=choices.sources, null=True, blank=True, verbose_name=_('Source'))
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files', verbose_name=_('Person'))
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True, allow_unicode=True)
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)

    @property
    def price_per_meter(self):
        return int(self.price_announced/self.area)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_status = SaleFile.objects.get(pk=self.pk).status
            if old_status == 'pen' and self.status == 'acc':
                self.datetime_expired = timezone.now() + timezone.timedelta(days=60)
        else:
            if self.status == 'acc':
                self.datetime_expired = timezone.now() + timezone.timedelta(days=60)
        if not self.unique_url_id:
            self.unique_url_id = generate_unique_id()
        if not self.code:
            self.code = generate_unique_code()
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super(SaleFile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.unique_url_id}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('sale_file_detail', args=[self.slug, self.unique_url_id])


class RentFile(models.Model):
    # location fields
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files', verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files', verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files', verbose_name=_('District'))
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files', verbose_name=_('Sub-District'))
    address = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Address'))
    # general characteristics
    deposit_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Deposit'))
    deposit_min = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Min Deposit'))
    rent_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Rent'))
    rent_min = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Min Rent'))
    convertable = models.CharField(max_length=15, choices=choices.beings, verbose_name=_('Convertable'))
    room = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Number of Rooms'))
    area = models.PositiveIntegerField(verbose_name=_('Area'))
    age = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Age of Apartment'))
    document = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Document'))
    level = models.CharField(max_length=15, choices=choices.levels, verbose_name=_('Level'))
    parking = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Parking'))
    elevator = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Elevator'))
    warehouse = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Warehouse'))
    # media
    image1 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 1'))
    image2 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 2'))
    image3 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 3'))
    image4 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 4'))
    image5 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 5'))
    image6 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 6'))
    image7 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 7'))
    image8 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 8'))
    image9 = models.ImageField(upload_to='files/images/', null=True, blank=True, verbose_name=_('Image 9'))
    video = models.FileField(upload_to='videos/', null=True, blank=True, verbose_name=_('Video'))
    has_image = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, default='hasnt', verbose_name=_('Has Image?'))
    has_video = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, default='hasnt', verbose_name=_('Has Video?'))
    # optional
    direction = models.CharField(max_length=15, choices=choices.directions, null=True, blank=True, verbose_name=_('Direction'))
    file_levels = models.CharField(max_length=15, choices=choices.levels, null=True, blank=True, verbose_name=_('Levels Number'))
    apartments_per_level = models.CharField(max_length=15, choices=choices.apartments_per_level, null=True, blank=True, verbose_name=_('Apartments per Level'))
    restoration = models.CharField(max_length=15, choices=choices.restorations, null=True, blank=True, verbose_name=_('Restoration'))
    bench_stove = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, verbose_name=_('Bench Stove'))
    balcony = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True, verbose_name=_('Balcony'))
    toilet = models.CharField(max_length=15, choices=choices.toilets, null=True, blank=True, verbose_name=_('Toilet'))
    hot_water = models.CharField(max_length=15, choices=choices.hot_water, null=True, blank=True, verbose_name=_('Hot Water System'))
    cooling = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Cooling System'))
    heating = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Heating System'))
    floor = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Floor Type'))
    # general information
    title = models.CharField(max_length=230, verbose_name=_('Title'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    source = models.CharField(max_length=15, choices=choices.sources, null=True, blank=True, verbose_name=_('Source'))
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files', verbose_name=_('Person'))
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True, allow_unicode=True)
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_status = RentFile.objects.get(pk=self.pk).status
            if old_status == 'pen' and self.status == 'acc':
                self.datetime_expired = timezone.now() + timezone.timedelta(days=60)
        else:
            if self.status == 'acc':
                self.datetime_expired = timezone.now() + timezone.timedelta(days=60)
        if not self.unique_url_id:
            self.unique_url_id = generate_unique_id()
        if not self.code:
            self.code = generate_unique_code()
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super(RentFile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.unique_url_id}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('rent_file_detail', args=[self.slug, self.unique_url_id])


# --------------------------------- SERVs --------------------------------
class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    budget_announced = models.PositiveBigIntegerField(verbose_name=_('Announced Budget'))
    budget_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Budget'))
    budget_status = models.CharField(max_length=15, choices=choices.budgets, default='1', verbose_name=_('Max Age'))
    room_min = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Min Rooms'))
    room_max = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Max Rooms'))
    area_min = models.PositiveIntegerField(default='1', verbose_name=_('Min Area'))
    area_max = models.PositiveIntegerField(default='1', verbose_name=_('Max Area'))
    age_min = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Min Age'))
    age_max = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Max Age'))
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Description'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} / {self.code} / {self.budget_announced}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('customer_detail', args=[self.code])


class Visit(models.Model):
    DATES = next_seven_days_shamsi
    sale_file = models.ForeignKey(SaleFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits', verbose_name=_('Sale File'))
    rent_file = models.ForeignKey(RentFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits', verbose_name=_('Rent File'))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='visits', verbose_name=_('Customer'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    date = models.CharField(max_length=200, choices=DATES, verbose_name=_('Date of Visit'))
    time = models.CharField(max_length=200, choices=choices.times, verbose_name=_('Time of Visit'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.serv_statuses, default='sub', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if self.sale_file:
            self.type = choices.types[0]
        if self.rent_file:
            self.type = choices.types[1]
        if not self.code:
            self.code = generate_unique_code()
        super(Visit, self).save(*args, **kwargs)

    def __str__(self):
        if self.sale_file:
            return f'{self.sale_file} / {self.code}'
        if self.rent_file:
            return f'{self.rent_file} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('visit_detail', args=[self.code])


class Session(models.Model):
    DATES = next_seven_days_shamsi
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions', verbose_name=_('Related Visit'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    date = models.CharField(max_length=200, choices=DATES, verbose_name=_('Date of Visit'))
    time = models.CharField(max_length=200, choices=choices.times, verbose_name=_('Time of Visit'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.serv_statuses, default='sub', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        self.type = self.visit.type
        if not self.code:
            self.code = generate_unique_code()
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        if self.visit.sale_file:
            return f'{self.visit.sale_file} / {self.code}'
        if self.visit.rent_file:
            return f'{self.visit.rent_file} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('session_detail', args=[self.code])


class Trade(models.Model):
    DATES = last_month_shamsi
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='trades', verbose_name=_('Related Session'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    date = models.CharField(max_length=200, choices=DATES, verbose_name=_('Date of Trade'))
    price = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Price'))
    deposit = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Deposit'))
    rent = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Rent'))
    owner = models.CharField(max_length=100, verbose_name=_('Owner (Seller / Lessor)'))
    owner_national_code = models.CharField(max_length=10, verbose_name=_('Owner (Seller / Lessor) National Code'))
    customer = models.CharField(max_length=100, verbose_name=_('Customer (Buyer / Tenant)'))
    customer_national_code = models.CharField(max_length=10, verbose_name=_('Customer (Buyer / Tenant) National Code'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    followup_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Followup Code'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        self.type = self.session.type
        if not self.code:
            self.code = generate_unique_code()
        super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        if self.session.visit.sale_file:
            return f'{self.session.visit.sale_file} / {self.code}'
        if self.session.visit.rent_file:
            return f'{self.session.visit.rent_file} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('trade_detail', args=[self.code])


# --------------------------------- MNGs --------------------------------
class Task(models.Model):
    DATES = next_month_shamsi
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    deadline = models.CharField(max_length=200, choices=DATES, verbose_name=_('Deadline'))
    type = models.CharField(max_length=10, choices=choices.task_types,  verbose_name=_('Type of Task'))
    agent = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Agent'))
    sale_file = models.ForeignKey(SaleFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Sale File'))
    rent_file = models.ForeignKey(RentFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Rent File'))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Customer'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    status = models.CharField(max_length=10, choices=choices.task_statuses, default='OP',  verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.agent.title} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.code])



