import os
import zipfile

import random
import string

import jdatetime
from jdatetime import timedelta, datetime
from datetime import datetime
from django.utils import timezone

from django.db import models
from django.db.models import Count, Q, F, PositiveBigIntegerField
from django.db.models.functions import Cast

from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.translation import gettext as _

from . import choices


# -------------------------------- CODEs ---------------------------------
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_unique_code():
    return ''.join(random.choices(string.digits + string.digits, k=6))


def generate_unique_code_longer():
    return ''.join(random.choices(string.digits + string.digits, k=10))


# -------------------------------- TIMEs ---------------------------------
def next_week_shamsi():
    days = []
    today = datetime.today()
    for i in range(0, 7):
        next_day = today + timedelta(days=i)
        weekday_en = next_day.strftime('%A')
        date_str = next_day.strftime('%Y/%m/%d')
        weekday_fa = {
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه',
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
        }.get(weekday_en, weekday_en)
        label = f"{weekday_fa} | {date_str}"
        days.append((date_str, label))
    return days


def last_and_next_week_shamsi():
    days = []
    today = datetime.today()
    for i in range(-7, 8):
        target_day = today + timedelta(days=i)
        weekday_en = target_day.strftime('%A')
        date_str = target_day.strftime('%Y/%m/%d')
        weekday_fa = {
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه',
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
        }.get(weekday_en, weekday_en)
        if i == 0:
            label = f"{weekday_fa} | {date_str} (امروز)"
        else:
            label = f"{weekday_fa} | {date_str}"
        days.append((date_str, label))
    return days


def next_month_shamsi():
    days = []
    today = datetime.today()
    for i in range(0, 30):
        next_day = today + timedelta(days=i)
        weekday_en = next_day.strftime('%A')
        date_str = next_day.strftime('%Y/%m/%d')
        weekday_fa = {
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه',
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
        }.get(weekday_en, weekday_en)
        label = f"{weekday_fa} | {date_str}"
        days.append((date_str, label))
    return days


def last_month_shamsi():
    days = []
    today = datetime.today()
    for i in range(0, 31):
        prev_day = today - timedelta(days=i)
        weekday_en = prev_day.strftime('%A')
        date_str = prev_day.strftime('%Y/%m/%d')
        weekday_fa = {
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه',
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه',
        }.get(weekday_en, weekday_en)
        label = f"{weekday_fa} | {date_str}"
        days.append((date_str, label))
    return days


# --------------------------------- LOCs ------------------------------------
class Province(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Province'))

    class Meta:
        verbose_name = 'استان'
        verbose_name_plural = 'استان‌ها'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('province_detail', args=[self.pk, self.name])


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('City'))
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')

    class Meta:
        verbose_name = 'شهر'
        verbose_name_plural = 'شهرها'

    @property
    def slug(self):
        return slugify(self.name, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('city_detail', args=[self.pk, self.name])


class District(models.Model):
    name = models.CharField(max_length=100, default='', verbose_name=_('District Name'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts')

    class Meta:
        verbose_name = 'محله (منطقه)'
        verbose_name_plural = 'محلات (مناطق)'

    @property
    def slug(self):
        return slugify(self.name, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('district_detail', args=[self.pk, self.name])


class SubDistrict(models.Model):
    name = models.CharField(max_length=100, default='', verbose_name=_('Sub-District Name'))
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sub_districts')
    description = models.TextField(max_length=1000, blank=True, null=True, default='', verbose_name=_('Description'))

    class Meta:
        verbose_name = 'زیرمحله'
        verbose_name_plural = 'زیرمحلات'

    @property
    def slug(self):
        return slugify(self.name, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('sub_district_detail', args=[self.pk, self.name])


# --------------------------------- CUM -------------------------------------
class CustomUserModel(AbstractUser):
    TITLE_CHOICES = [
        ('bs', _('Boss')),
        ('fp', _('File Person')),
        ('cp', _('Customer Person')),
        ('bt', _('Dual Person')),
        ('nd', 'همه محلات'),  # NEW
    ]
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, null=True, verbose_name=_('Title'))
    name_family = models.CharField(max_length=300, blank=True, null=True, verbose_name='نام و نام خانوادگی')
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='agents', verbose_name=_('Sub-District'))
    email = models.EmailField(unique=False, blank=True, null=True)
    REQUIRED_FIELDS = []

    @property
    def is_boss(self):
        if self.title == 'bs':
            return choices.beings[0]
        else:
            return choices.beings[1]

    def get_absolute_url(self):
        return reverse('agent_detail', kwargs={'pk': self.pk, 'title': self.title, 'username': self.username})


# --------------------------------- FILEs -----------------------------------
class Person(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=150, blank=True, null=True, verbose_name=_('Description'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, null=True)
    delete_request = models.CharField(max_length=3, choices=choices.yes_or_no, blank=True, null=True, default='No',
                                      verbose_name=_('Delete Request'))
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='ایجاد شده توسط')

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'شخص آگهی‌دهنده'
        verbose_name_plural = 'اشخاص آگهی‌دهنده'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.pk])


class SaleFile(models.Model):
    # location fields
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files',
                                 verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files',
                             verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files',
                                 verbose_name=_('District'))
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='sale_files', verbose_name=_('Sub-District'))
    address = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Address'))
    street = models.CharField(max_length=15, blank=True, null=True, verbose_name='خیابان اصلی')
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
    # optional
    direction = models.CharField(max_length=15, choices=choices.directions, null=True, blank=True,
                                 verbose_name=_('Direction'))
    file_levels = models.CharField(max_length=15, choices=choices.levels, null=True, blank=True,
                                   verbose_name=_('Levels Number'))
    apartments_per_level = models.CharField(max_length=15, choices=choices.apartments_per_level, null=True, blank=True,
                                            verbose_name=_('Apartments per Level'))
    restoration = models.CharField(max_length=15, choices=choices.restorations, null=True, blank=True,
                                   verbose_name=_('Restoration'))
    bench_stove = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True,
                                   verbose_name=_('Bench Stove'))
    balcony = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True,
                               verbose_name=_('Balcony'))
    toilet = models.CharField(max_length=15, choices=choices.toilets, null=True, blank=True, verbose_name=_('Toilet'))
    hot_water = models.CharField(max_length=15, choices=choices.hot_water, null=True, blank=True,
                                 verbose_name=_('Hot Water System'))
    cooling = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Cooling System'))
    heating = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Heating System'))
    floor = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Floor Type'))
    # general information
    title = models.CharField(max_length=230, verbose_name=_('Title'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    source = models.CharField(max_length=15, choices=choices.sources, null=True, blank=True, verbose_name=_('Source'))
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files',
                               verbose_name=_('Person'))
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)
    delete_request = models.CharField(max_length=3, choices=choices.yes_or_no, blank=True, null=True, default='No',
                                      verbose_name=_('Delete Request'))
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale_files',
                                   verbose_name='ایجاد شده توسط')

    @property
    def price_per_meter(self):
        return int(self.price_announced / self.area)

    @property
    def has_images(self):
        if self.image1 or self.image2 or self.image3 or self.image4 or self.image5 or self.image6 or self.image7 or self.image8 or self.image9:
            return True

    @property
    def has_video(self):
        if self.video:
            return True

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
        super(SaleFile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.unique_url_id}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'فایل فروش'
        verbose_name_plural = 'فایل‌های فروش'

    def get_absolute_url(self):
        return reverse('sale_file_detail', args=[self.pk, self.unique_url_id])


class RentFile(models.Model):
    # location fields
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files',
                                 verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files',
                             verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files',
                                 verbose_name=_('District'))
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='rent_files', verbose_name=_('Sub-District'))
    address = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Address'))
    street = models.CharField(max_length=15, blank=True, null=True, verbose_name='خیابان اصلی')
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
    # optional
    direction = models.CharField(max_length=15, choices=choices.directions, null=True, blank=True,
                                 verbose_name=_('Direction'))
    file_levels = models.CharField(max_length=15, choices=choices.levels, null=True, blank=True,
                                   verbose_name=_('Levels Number'))
    apartments_per_level = models.CharField(max_length=15, choices=choices.apartments_per_level, null=True, blank=True,
                                            verbose_name=_('Apartments per Level'))
    restoration = models.CharField(max_length=15, choices=choices.restorations, null=True, blank=True,
                                   verbose_name=_('Restoration'))
    bench_stove = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True,
                                   verbose_name=_('Bench Stove'))
    balcony = models.CharField(max_length=15, choices=choices.booleans, null=True, blank=True,
                               verbose_name=_('Balcony'))
    toilet = models.CharField(max_length=15, choices=choices.toilets, null=True, blank=True, verbose_name=_('Toilet'))
    hot_water = models.CharField(max_length=15, choices=choices.hot_water, null=True, blank=True,
                                 verbose_name=_('Hot Water System'))
    cooling = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Cooling System'))
    heating = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Heating System'))
    floor = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Floor Type'))
    # general information
    title = models.CharField(max_length=230, verbose_name=_('Title'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    source = models.CharField(max_length=15, choices=choices.sources, null=True, blank=True, verbose_name=_('Source'))
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files',
                               verbose_name=_('Person'))
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)
    delete_request = models.CharField(max_length=3, choices=choices.yes_or_no, blank=True, null=True, default='No',
                                      verbose_name=_('Delete Request'))
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='rent_files',
                                   verbose_name='ایجاد شده توسط')

    @property
    def has_images(self):
        if self.image1 or self.image2 or self.image3 or self.image4 or self.image5 or self.image6 or self.image7 or self.image8 or self.image9:
            return True

    @property
    def has_video(self):
        if self.video:
            return True

    @property
    def zip_file(self):
        """Generates and returns the URL of a ZIP file containing all available media."""
        media_files = [self.image1, self.image2, self.image3, self.image4, self.image5,
                       self.image6, self.image7, self.image8, self.image9, self.video]

        # Filter out None values (blank images/videos)
        media_files = [file for file in media_files if file]
        if not media_files:
            return None

        # Define ZIP file path
        zip_filename = f"sale_{self.id}_media.zip"
        zip_folder = os.path.join(settings.MEDIA_ROOT, "temp_zips")
        os.makedirs(zip_folder, exist_ok=True)  # Ensure directory exists
        zip_path = os.path.join(zip_folder, zip_filename)

        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for media in media_files:
                media_path = os.path.join(settings.MEDIA_ROOT, str(media))
                if os.path.exists(media_path):
                    zipf.write(media_path, os.path.basename(media_path))

        # Return URL of the ZIP file
        return f"{settings.MEDIA_URL}temp_zips/{zip_filename}"

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
        super(RentFile, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} / {self.unique_url_id}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'فایل اجاره'
        verbose_name_plural = 'فایل‌های اجاره'

    def get_absolute_url(self):
        return reverse('rent_file_detail', args=[self.pk, self.unique_url_id])


class Buyer(models.Model):
    # locations
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers',
                                 verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers',
                             verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers',
                                 verbose_name=_('District'))
    sub_districts = models.ManyToManyField(SubDistrict, blank=True, related_name='buyers',  verbose_name=_('Sub-Districts'))
    # properties
    budget_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Budget'))
    budget_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Budget'))
    budget_status = models.CharField(max_length=15, choices=choices.budgets, blank=True, null=True,
                                     verbose_name=_('Budget Status'))
    room_min = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Min Rooms'))
    room_max = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Max Rooms'))
    area_min = models.PositiveIntegerField(default='1', verbose_name=_('Min Area'))
    area_max = models.PositiveIntegerField(default='1', verbose_name=_('Max Area'))
    age_min = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Min Age'))
    age_max = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Max Age'))
    document = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Document'))
    parking = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Parking'))
    elevator = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Elevator'))
    warehouse = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Warehouse'))
    # info
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Description'))
    code = models.CharField(max_length=10, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date and Time of Creation'))
    delete_request = models.CharField(max_length=3, choices=choices.yes_or_no, blank=True, null=True, default='No',
                                      verbose_name=_('Delete Request'))
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers',
                                   verbose_name='ایجاد شده توسط')

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code_longer()
        super(Buyer, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} / {self.code} / {self.budget_announced}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'خریدار'
        verbose_name_plural = 'خریداران'

    def get_absolute_url(self):
        return reverse('buyer_detail', args=[self.pk, self.code])


class Renter(models.Model):
    # locations
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters',
                                 verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters',
                             verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters',
                                 verbose_name=_('District'))
    sub_districts = models.ManyToManyField(SubDistrict, blank=True, related_name='renters',  verbose_name=_('Sub-Districts'))
    # properties
    deposit_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Deposit'))
    deposit_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Deposit'))
    rent_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Rent'))
    rent_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Rent'))
    budget_status = models.CharField(max_length=15, choices=choices.budgets, blank=True, null=True,
                                     verbose_name=_('Budget Status'))
    convertable = models.CharField(max_length=15, choices=choices.beings, verbose_name=_('Convertable'))
    room_min = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Min Rooms'))
    room_max = models.CharField(max_length=15, choices=choices.rooms, verbose_name=_('Max Rooms'))
    area_min = models.PositiveIntegerField(default='1', verbose_name=_('Min Area'))
    area_max = models.PositiveIntegerField(default='1', verbose_name=_('Max Area'))
    age_min = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Min Age'))
    age_max = models.CharField(max_length=15, choices=choices.ages, default='1', verbose_name=_('Max Age'))
    document = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Document'))
    parking = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Parking'))
    elevator = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Elevator'))
    warehouse = models.CharField(max_length=15, choices=choices.booleans, verbose_name=_('Warehouse'))
    # info
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Description'))
    code = models.CharField(max_length=10, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date and Time of Creation'))
    delete_request = models.CharField(max_length=3, choices=choices.yes_or_no, blank=True, null=True, default='No',
                                      verbose_name=_('Delete Request'))
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters',
                                   verbose_name='ایجاد شده توسط')

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code_longer()
        super(Renter, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} / {self.code} / {self.deposit_announced} / {self.rent_announced}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'مستاجر'
        verbose_name_plural = 'مستاجران'

    def get_absolute_url(self):
        return reverse('renter_detail', args=[self.pk, self.code])


# --------------------------------- SERVs ----------------------------------
class Session(models.Model):
    agent = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='sessions', verbose_name=_('Agent'))
    sale_file_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Sale File Code'))
    sale_file = models.ForeignKey(SaleFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions',
                                  verbose_name=_('Visit Sale File'))
    rent_file_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Rent File Code'))
    rent_file = models.ForeignKey(RentFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions',
                                  verbose_name=_('Visit Rent File'))
    buyer_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('Buyer Code'))
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions',
                              verbose_name=_('Visit Buyer'))
    renter_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('Renter Code'))
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions',
                               verbose_name=_('Visit Renter'))
    type = models.CharField(max_length=10, choices=choices.types, blank=True, null=True,
                            verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    boss_notes = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Boss Notes'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    boss_final_comment = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Boss Final Comment'))
    date = models.CharField(max_length=200, verbose_name=_('Date of Visit'))
    time = models.CharField(max_length=200, choices=choices.times, verbose_name=_('Time of Visit'))
    code = models.CharField(max_length=10, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.serv_statuses, default='sub', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.sale_file and self.sale_file_code:
            self.sale_file = SaleFile.objects.get(code=self.sale_file_code)
        if not self.rent_file and self.rent_file_code:
            self.rent_file = RentFile.objects.get(code=self.rent_file_code)
        if not self.buyer and self.buyer_code:
            self.buyer = Buyer.objects.get(code=self.buyer_code)
        if not self.renter and self.renter_code:
            self.renter = Renter.objects.get(code=self.renter_code)
        if not self.code:
            self.code = generate_unique_code_longer()
        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous = Session.objects.filter(pk=self.pk).first()
            if previous:
                previous_status = previous.status
        super(Session, self).save(*args, **kwargs)
        if self.status == 'dne' and previous_status != 'dne':
            if not TaskBoss.objects.filter(result_session=self).exists():
                TaskBoss.objects.create(result_session=self, type='rs')

    def __str__(self):
        return f'نشست: {self.get_type_display()} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'نشست'
        verbose_name_plural = 'نشست‌ها'

    def get_absolute_url(self):
        return reverse('session_detail', args=[self.pk, self.code])


class Trade(models.Model):
    session_code = models.CharField(max_length=10, null=True, unique=True, blank=True, verbose_name='کد جلسه')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='trades',
                                verbose_name='جلسه')
    type = models.CharField(max_length=10, choices=choices.types, blank=True, null=True,
                            verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    date = models.CharField(max_length=200, verbose_name=_('Date of Trade'))
    price = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Price'))
    deposit = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Deposit'))
    rent = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Rent'))
    contract_owner = models.CharField(max_length=200, blank=True, null=True,
                                      verbose_name='نام فروشنده / موجر (قرارداد)')
    contract_buyer = models.CharField(max_length=200, blank=True, null=True,
                                      verbose_name='نام خریدار (قرارداد)')
    contract_renter = models.CharField(max_length=200, blank=True, null=True,
                                       verbose_name='نام مستاجر (قرارداد)')
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    followup_code = models.CharField(max_length=20, null=True, unique=True, blank=True, verbose_name='کد رهگیری')
    followup_code_status = models.CharField(max_length=10, choices=choices.fc_statuses, default='ntk',
                                            verbose_name='وضعیت کد رهگیری')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sale_file(self):
        if self.type == 'sale' and self.session:
            file = self.session.sale_file
            return file

    @property
    def rent_file(self):
        if self.type == 'rent' and self.session:
            file = self.session.rent_file
            return file

    @property
    def buyer(self):
        if self.type == 'sale' and self.session:
            buyer = self.session.buyer
            return buyer

    @property
    def renter(self):
        if self.type == 'rent' and self.session:
            renter = self.session.renter
            return renter

    def save(self, *args, **kwargs):
        if not self.session:
            self.session = Session.objects.get(code=self.session_code)
        if self.followup_code:
            self.followup_code_status = choices.fc_statuses[0][0]
        else:
            self.followup_code_status = choices.fc_statuses[1][0]
        if not self.code:
            self.code = generate_unique_code()
        super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        if self.session:
            if self.type == 'sale':
                return f'معامله: {self.get_type_display()} / {self.code} / {self.session.sale_file}'
            else:
                return f'معامله: {self.get_type_display()} / {self.code} / {self.session.rent_file}'
        else:
            return f'معامله: {self.get_type_display()} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'معامله'
        verbose_name_plural = 'معاملات'

    def get_absolute_url(self):
        return reverse('trade_detail', args=[self.pk, self.code])


# --------------------------------- USERs ---------------------------------
class TaskBoss(models.Model):
    new_sale_file = models.ForeignKey(SaleFile, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='new_sale_files', verbose_name='فایل فروش جدید')
    new_rent_file = models.ForeignKey(RentFile, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='new_rent_files', verbose_name='فایل اجاره جدید')
    new_buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, blank=True, null=True,
                                  related_name='new_buyers', verbose_name='خریدار جدید')
    new_renter = models.ForeignKey(Renter, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='new_renter', verbose_name='مستاجر جدید')
    new_person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True,
                                   related_name='new_persons', verbose_name='آگهی‌دهنده جدید')
    new_session = models.ForeignKey(Session, on_delete=models.CASCADE, blank=True, null=True,
                                    related_name='new_sessions', verbose_name='نشست جدید')
    result_session = models.ForeignKey(Session, on_delete=models.CASCADE, blank=True, null=True,
                                       related_name='result_sessions', verbose_name='نتیجه نشست')
    type = models.CharField(max_length=10, choices=choices.boss_task_types, blank=True, null=True, verbose_name='نوع')
    condition = models.CharField(max_length=10, choices=choices.boss_task_statuses, default='op', blank=True, null=True,
                                 verbose_name='وضعیت وظیفه مدیر')
    code = models.CharField(max_length=10, null=True, unique=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def agent(self):
        if self.new_sale_file:
            return getattr(self.new_sale_file, 'created_by', None)
        elif self.new_rent_file:
            return getattr(self.new_rent_file, 'created_by', None)
        elif self.new_buyer:
            return getattr(self.new_buyer, 'created_by', None)
        elif self.new_renter:
            return getattr(self.new_renter, 'created_by', None)
        elif self.new_person:
            return getattr(self.new_person, 'created_by', None)
        return None

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code_longer()
        super(TaskBoss, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.get_type_display()} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'وظیفه مدیریتی'
        verbose_name_plural = 'وظایف مدیریتی'

    def get_absolute_url(self):
        return reverse('boss_task_approve', args=[self.pk, self.code])


class Reminder(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    date = models.CharField(max_length=200, verbose_name=_('Deadline'))
    agent = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders',
                              verbose_name=_('Agent'))
    sale_file_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Sale File Code'))
    sale_file = models.ForeignKey(SaleFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders',
                                  verbose_name='فایل فروش')
    rent_file_code = models.CharField(max_length=6, null=True, blank=True, verbose_name=_('Rent File Code'))
    rent_file = models.ForeignKey(RentFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders',
                                  verbose_name='فایل اجاره')
    buyer_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('Buyer Code'))
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders',
                              verbose_name='خریدار')
    renter_code = models.CharField(max_length=10, null=True, blank=True, verbose_name=_('Renter Code'))
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, null=True, blank=True, related_name='reminders',
                               verbose_name='مستاجر')
    code = models.CharField(max_length=10, null=True, unique=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    status = models.CharField(max_length=10, choices=choices.reminder_statuses, default='OP', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sub_district(self):
        return self.agent.sub_district

    def save(self, *args, **kwargs):
        if not self.sale_file and self.sale_file_code:
            self.sale_file = SaleFile.objects.get(code=self.sale_file_code)
        if not self.rent_file and self.rent_file_code:
            self.rent_file = RentFile.objects.get(code=self.rent_file_code)
        if not self.buyer and self.buyer_code:
            self.buyer = Buyer.objects.get(code=self.buyer_code)
        if not self.renter and self.renter_code:
            self.renter = Renter.objects.get(code=self.renter_code)
        if not self.code:
            self.code = generate_unique_code_longer()
        super(Reminder, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.agent} / {self.date} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'یادآور'
        verbose_name_plural = 'یادآورها'

    def get_absolute_url(self):
        return reverse('reminder_detail', args=[self.pk, self.code])


class Mark(models.Model):
    sale_file = models.ForeignKey(SaleFile, on_delete=models.CASCADE, blank=True, null=True,
                                  related_name='marks', verbose_name='فایل فروش نشان‌شده')
    rent_file = models.ForeignKey(RentFile, on_delete=models.CASCADE, blank=True, null=True,
                                  related_name='marks', verbose_name='فایل اجاره نشان‌شده')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, blank=True, null=True,
                              related_name='marks', verbose_name='خریدار نشان‌شده')
    renter = models.ForeignKey(Renter, on_delete=models.CASCADE, blank=True, null=True,
                               related_name='marks', verbose_name='مستاجر نشان‌شده')
    agent = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='marks', verbose_name='مشاور')
    type = models.CharField(max_length=10, choices=choices.mark_types, verbose_name='نوع نشان‌شده')
    code = models.CharField(max_length=10, null=True, blank=True)
    slug = models.SlugField(max_length=150, blank=True, verbose_name='اسلاگ')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code_longer()
        if self.sale_file:
            self.type = choices.mark_types[0][0]
        if self.rent_file:
            self.type = choices.mark_types[1][0]
        if self.buyer:
            self.type = choices.mark_types[2][0]
        if self.renter:
            self.type = choices.mark_types[3][0]
        self.slug = slugify(self.agent.username)
        super(Mark, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.agent} / {self.get_type_display()} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'نشان‌شده'
        verbose_name_plural = 'نشان‌شده‌ها'

    def get_absolute_url(self):
        return reverse('mark_detail', args=[self.pk])


# --------------------------------- TEAMs ---------------------------------
class Report(models.Model):
    agent = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_reports',
                              verbose_name='مشاور')
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='توضیحات')
    boss_note = models.TextField(max_length=1000, blank=True, null=True, verbose_name='توضیحات مدیر')
    status = models.CharField(max_length=10, choices=choices.report_statuses, default='wfb', verbose_name='وضعیت')
    date = models.CharField(max_length=200, verbose_name='تاریخ')

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not self.agent and user:
            self.agent = user
        if not self.date:
            jalali_now = jdatetime.datetime.now()
            self.date = jalali_now.strftime('%Y/%m/%d')
        super().save(*args, **kwargs)
        if self.agent and self.date:
            daily_status, created = DailyTaskStatus.objects.get_or_create(
                agent=self.agent,
                date=self.date
            )
            daily_status.update_from_report(self)

    class Meta:
        verbose_name = 'گزارش'
        verbose_name_plural = 'گزارش‌ها'
        ordering = ['-date']

    def __str__(self):
        if self.agent.name_family:
            return f"گزارش روزانه: {self.agent.name_family} - {self.date}"
        else:
            return f"گزارش روزانه: {self.agent} - {self.date}"

    def get_absolute_url(self):
        return reverse('report_detail', args=[self.agent, self.date])


class ReportItem(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True, related_name='items', verbose_name='کزارش')
    file_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد فایل')
    customer_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد مشتری')
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='توضیحات')
    type = models.CharField(max_length=10, choices=choices.report_item_choices, verbose_name='نوع')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.report and self.report.pk and self.report.agent and self.report.date:
            daily_status, created = DailyTaskStatus.objects.get_or_create(
                agent=self.report.agent,
                date=self.report.date
            )
            daily_status.update_from_report(self.report)

    @property
    def file(self):
        sale_file_codes = (SaleFile.objects.exclude(delete_request='Yes').filter(status='acc')
                           .values('code').values_list('code', flat=True))
        rent_file_codes = (RentFile.objects.exclude(delete_request='Yes').filter(status='acc')
                           .values('code').values_list('code', flat=True))
        if self.file_code in sale_file_codes:
            file = SaleFile.objects.get(code=self.file_code)
            return file
        if self.file_code in rent_file_codes:
            file = RentFile.objects.get(code=self.file_code)
            return file
        return None

    @property
    def customer(self):
        buyer_codes = (Buyer.objects.exclude(delete_request='Yes').filter(status='acc')
                           .values('code').values_list('code', flat=True))
        renter_codes = (Renter.objects.exclude(delete_request='Yes').filter(status='acc')
                           .values('code').values_list('code', flat=True))
        if self.customer_code in buyer_codes:
            customer = Buyer.objects.get(code=self.customer_code)
            return customer
        if self.customer_code in renter_codes:
            customer = Renter.objects.get(code=self.customer_code)
            return customer
        return None

    class Meta:
        verbose_name = 'آگهی'
        verbose_name_plural = 'آگهی‌ها'
        ordering = ['-datetime_created']

    def __str__(self):
        if self.report.agent.name_family:
            return f"{self.report.agent.name_family} - {self.file_code}"
        else:
            return f"{self.report.agent} - {self.file_code}"

    def get_absolute_url(self):
        if self.file_code:
            return reverse('report_item_detail', args=[self.pk, self.type, self.file_code])
        elif self.customer_code:
            return reverse('report_item_detail', args=[self.pk, self.type, self.customer_code])
        else:
            return reverse('report_item_detail', args=[self.pk, self.type])


class Announcement(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='created_announcements', verbose_name='منشا')
    visible_to = models.ManyToManyField(CustomUserModel, blank=True, related_name='visible_announcements', verbose_name='مخاطب')
    viewed_by = models.ManyToManyField(CustomUserModel, blank=True, related_name='viewed_announcements', verbose_name='بیننده')
    announcement_type = models.CharField(max_length=20, choices=choices.announcement_types, verbose_name='نوع')
    is_active = models.BooleanField(default=True, verbose_name='فعال بودن')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='زمان ساخت')

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-datetime_created']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-datetime_created']),
        ]

    def __str__(self):
        return f"اعلان: {self.announcement_type} - {self.object_id}"

    def get_agents_with_suggestions(self):
        agents_with_suggestions = []
        creator = self.created_by

        if self.announcement_type == 'sf':
            sale_file = self.content_object
            matching_buyers = Buyer.objects.filter(
                status='acc',
                budget_announced__gt=0.9 * sale_file.price_announced,
                budget_announced__lt=1.1 * sale_file.price_announced,
                area_min__lt=1.2 * sale_file.area,
                area_max__gt=0.8 * sale_file.area
            ).exclude(
                delete_request='Yes'
            ).exclude(
                created_by=creator
            ).values_list('created_by', flat=True).distinct()
            agents_with_suggestions = list(matching_buyers)

        elif self.announcement_type == 'rf':
            rent_file = self.content_object
            base_queryset = Renter.objects.annotate(
                deposit_total_calc=Cast(
                    F('deposit_announced') + (100 * F('rent_announced') / 3),
                    PositiveBigIntegerField()
                )
            ).exclude(
                delete_request='Yes'
            ).exclude(
                created_by=creator
            )

            non_convertable = base_queryset.filter(
                status='acc',
                convertable='isnt',
                deposit_announced__gt=0.8 * rent_file.deposit_announced,
                deposit_announced__lt=1.2 * rent_file.deposit_announced,
                rent_announced__gt=0.8 * rent_file.rent_announced,
                rent_announced__lt=1.2 * rent_file.rent_announced,
                area_min__lt=1.2 * rent_file.area,
                area_max__gt=0.8 * rent_file.area
            )

            rent_total_min = 0.8 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
            rent_total_max = 1.2 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))

            convertable = base_queryset.filter(
                status='acc',
                convertable='is',
                deposit_total_calc__gt=rent_total_min,
                deposit_total_calc__lt=rent_total_max,
                area_min__lt=1.2 * rent_file.area,
                area_max__gt=0.8 * rent_file.area
            )

            matching_renters = (non_convertable | convertable).values_list('created_by', flat=True).distinct()
            agents_with_suggestions = list(matching_renters)

        elif self.announcement_type == 'by':
            buyer = self.content_object
            price_min = 0.9 * buyer.budget_announced
            price_max = 1.1 * buyer.budget_announced
            area_min = 0.8 * buyer.area_min
            area_max = 1.2 * buyer.area_max

            query = SaleFile.objects.filter(
                status='acc',
                price_announced__gt=price_min,
                price_announced__lt=price_max,
                area__gt=area_min,
                area__lt=area_max
            ).exclude(
                delete_request='Yes'
            ).exclude(
                created_by=creator
            )
            matching_files = query.values_list('created_by', flat=True).distinct()
            agents_with_suggestions = list(matching_files)

        elif self.announcement_type == 'rt':
            renter = self.content_object
            deposit_min = 0.8 * renter.deposit_announced
            deposit_max = 1.2 * renter.deposit_announced
            rent_min = 0.8 * renter.rent_announced
            rent_max = 1.2 * renter.rent_announced
            area_min = 0.8 * renter.area_min
            area_max = 1.2 * renter.area_max
            renter_total_min = 0.8 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))
            renter_total_max = 1.2 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))

            base_queryset = RentFile.objects.annotate(
                deposit_total_calc=Cast(
                    F('deposit_announced') + (100 * F('rent_announced') / 3),
                    PositiveBigIntegerField()
                )
            ).exclude(
                delete_request='Yes'
            ).exclude(
                created_by=creator
            )

            non_convertable = base_queryset.filter(
                status='acc',
                convertable='isnt',
                deposit_announced__gt=deposit_min,
                deposit_announced__lt=deposit_max,
                rent_announced__gt=rent_min,
                rent_announced__lt=rent_max,
                area__gt=area_min,
                area__lt=area_max
            )

            convertable = base_queryset.filter(
                status='acc',
                convertable='is',
                deposit_total_calc__gt=renter_total_min,
                deposit_total_calc__lt=renter_total_max,
                area__gt=area_min,
                area__lt=area_max
            )

            query = (non_convertable | convertable).distinct()
            matching_files = query.values_list('created_by', flat=True).distinct()
            agents_with_suggestions = list(matching_files)

        return CustomUserModel.objects.filter(id__in=agents_with_suggestions)

    def get_suggestions_for_agent(self, agent):
        creator = self.created_by

        if self.announcement_type == 'sf':
            sale_file = self.content_object
            suggestions = Buyer.objects.filter(
                created_by=agent,
                status='acc',
                budget_announced__gt=0.9 * sale_file.price_announced,
                budget_announced__lt=1.1 * sale_file.price_announced,
                area_min__lt=1.2 * sale_file.area,
                area_max__gt=0.8 * sale_file.area
            ).exclude(delete_request='Yes')

            # Exclude already sent buyers by this agent for this announcement
            buyer_ct = ContentType.objects.get_for_model(Buyer)
            already_sent_ids = InteractionItem.objects.filter(
                interaction__announcement=self,
                interaction__sender=agent,
                content_type=buyer_ct
            ).values_list('object_id', flat=True)

            if already_sent_ids:
                suggestions = suggestions.exclude(id__in=already_sent_ids)

            return suggestions

        elif self.announcement_type == 'rf':
            rent_file = self.content_object
            base_queryset = Renter.objects.filter(
                created_by=agent
            ).annotate(
                deposit_total_calc=Cast(
                    F('deposit_announced') + (100 * F('rent_announced') / 3),
                    PositiveBigIntegerField()
                )
            ).exclude(delete_request='Yes')

            non_convertable = base_queryset.filter(
                status='acc',
                convertable='isnt',
                deposit_announced__gt=0.8 * rent_file.deposit_announced,
                deposit_announced__lt=1.2 * rent_file.deposit_announced,
                rent_announced__gt=0.8 * rent_file.rent_announced,
                rent_announced__lt=1.2 * rent_file.rent_announced,
                area_min__lt=1.2 * rent_file.area,
                area_max__gt=0.8 * rent_file.area
            )

            rent_total_min = 0.8 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
            rent_total_max = 1.2 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))

            convertable = base_queryset.filter(
                status='acc',
                convertable='is',
                deposit_total_calc__gt=rent_total_min,
                deposit_total_calc__lt=rent_total_max,
                area_min__lt=1.2 * rent_file.area,
                area_max__gt=0.8 * rent_file.area
            )

            suggestions = (non_convertable | convertable).distinct()

            # Exclude already sent renters by this agent for this announcement
            renter_ct = ContentType.objects.get_for_model(Renter)
            already_sent_ids = InteractionItem.objects.filter(
                interaction__announcement=self,
                interaction__sender=agent,
                content_type=renter_ct
            ).values_list('object_id', flat=True)

            if already_sent_ids:
                suggestions = suggestions.exclude(id__in=already_sent_ids)

            return suggestions

        elif self.announcement_type == 'by':
            buyer = self.content_object
            price_min = 0.9 * buyer.budget_announced
            price_max = 1.1 * buyer.budget_announced
            area_min = 0.8 * buyer.area_min
            area_max = 1.2 * buyer.area_max

            suggestions = SaleFile.objects.filter(
                created_by=agent,
                status='acc',
                price_announced__gt=price_min,
                price_announced__lt=price_max,
                area__gt=area_min,
                area__lt=area_max
            ).exclude(delete_request='Yes')

            # Exclude already sent sale files by this agent for this announcement
            sale_file_ct = ContentType.objects.get_for_model(SaleFile)
            already_sent_ids = InteractionItem.objects.filter(
                interaction__announcement=self,
                interaction__sender=agent,
                content_type=sale_file_ct
            ).values_list('object_id', flat=True)

            if already_sent_ids:
                suggestions = suggestions.exclude(id__in=already_sent_ids)

            return suggestions

        elif self.announcement_type == 'rt':
            renter = self.content_object
            deposit_min = 0.8 * renter.deposit_announced
            deposit_max = 1.2 * renter.deposit_announced
            rent_min = 0.8 * renter.rent_announced
            rent_max = 1.2 * renter.rent_announced
            area_min = 0.8 * renter.area_min
            area_max = 1.2 * renter.area_max
            renter_total_min = 0.8 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))
            renter_total_max = 1.2 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))

            base_queryset = RentFile.objects.filter(
                created_by=agent
            ).annotate(
                deposit_total_calc=Cast(
                    F('deposit_announced') + (100 * F('rent_announced') / 3),
                    PositiveBigIntegerField()
                )
            ).exclude(delete_request='Yes')

            non_convertable = base_queryset.filter(
                status='acc',
                convertable='isnt',
                deposit_announced__gt=deposit_min,
                deposit_announced__lt=deposit_max,
                rent_announced__gt=rent_min,
                rent_announced__lt=rent_max,
                area__gt=area_min,
                area__lt=area_max
            )

            convertable = base_queryset.filter(
                status='acc',
                convertable='is',
                deposit_total_calc__gt=renter_total_min,
                deposit_total_calc__lt=renter_total_max,
                area__gt=area_min,
                area__lt=area_max
            )

            suggestions = (non_convertable | convertable).distinct()

            # Exclude already sent rent files by this agent for this announcement
            rent_file_ct = ContentType.objects.get_for_model(RentFile)
            already_sent_ids = InteractionItem.objects.filter(
                interaction__announcement=self,
                interaction__sender=agent,
                content_type=rent_file_ct
            ).values_list('object_id', flat=True)

            if already_sent_ids:
                suggestions = suggestions.exclude(id__in=already_sent_ids)

            return suggestions

        return None

    def get_remaining_suggestion_count_for_agent(self, agent):
        suggestions = self.get_suggestions_for_agent(agent)
        if suggestions:
            return suggestions.count()
        return 0

    def get_object_display(self):
        return str(self.content_object)

    def get_absolute_url(self):
        return reverse('announcement_detail', args=[self.pk])


class Interaction(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='interactions', verbose_name='اعلان')
    sender = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='sent_interactions', verbose_name='فرستنده')
    receiver = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='received_interactions', verbose_name='گیرنده')
    interaction_type = models.CharField(max_length=20, choices=choices.interaction_types, verbose_name='نوع')
    message = models.TextField(max_length=1000, blank=True, null=True, verbose_name='پبغام')
    status = models.CharField(max_length=20, choices=choices.interactions_statuses, default='unseen', verbose_name='وضعیت')
    datetime_viewed = models.DateTimeField(null=True, blank=True, verbose_name='زمان مشاهده')
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='زمان ساخت')

    class Meta:
        verbose_name = 'تعامل'
        verbose_name_plural = 'تعامل‌ها'
        ordering = ['-datetime_created']
        indexes = [
            models.Index(fields=['sender', '-datetime_created']),
            models.Index(fields=['receiver', '-datetime_created']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"تعامل از  {self.sender} به {self.receiver} - {self.interaction_type}"

    def get_absolute_url(self):
        return reverse('interaction_detail', args=[self.pk])


class InteractionItem(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE, related_name='items', verbose_name='تعامل')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    cached_price = models.PositiveBigIntegerField(null=True, blank=True, verbose_name='قیمت کش')
    cached_area = models.PositiveIntegerField(null=True, blank=True, verbose_name='متراژ کش')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت')

    class Meta:
        verbose_name = 'آیتم تعامل'
        verbose_name_plural = 'آیتم‌های تعامل'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['interaction', 'content_type']),
        ]

    def __str__(self):
        return f"آیتم در  {self.interaction.id} - {self.content_object}"


class NotifiedTask(models.Model):
    agent = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='notified_tasks', verbose_name='مشاور')
    date = models.CharField(max_length=50, blank=True, null=True, verbose_name='تاریخ')
    task_type = models.CharField(max_length=30, choices=choices.daily_task_types, verbose_name='نوع وظیفه')
    status = models.CharField(max_length=20, choices=choices.daily_task_statuses, default='waiting', verbose_name='وضعیت')
    result = models.TextField(blank=True, null=True, verbose_name='نتیجه')
    related_announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, null=True, blank=True,
                                             related_name='suggestion_tasks', verbose_name='اعلان مربوطه')
    related_interaction_item = models.ForeignKey(InteractionItem, on_delete=models.CASCADE, null=True, blank=True,
                                                 related_name='notified_tasks', verbose_name='آیتم تعاملی مربوطه')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان و تاریخ ایجاد')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان و تاریخ تکمیل')

    def save(self, *args, **kwargs):
        if not self.date:
            jalali_now = jdatetime.datetime.now()
            self.date = jalali_now.strftime('%Y/%m/%d')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'وظیفه'
        verbose_name_plural = 'وظایف'
        ordering = ['-created_at', 'status']
        indexes = [
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['task_type', 'status']),
        ]

    def __str__(self):
        return f"{self.agent} - {self.get_task_type_display()} - {self.get_status_display()}"

    def mark_as_done(self, result=None):
        self.completed_at = timezone.now()
        if result:
            self.result = result
        self.status = 'done'
        self.save()

    def get_suggestion_count(self):
        if self.task_type == 'announcement_suggestions' and self.related_announcement:
            return self.related_announcement.get_suggestions_for_agent(self.agent).count()
        return 0

    def get_target_agents_count(self):
        if self.task_type == 'announcement_suggestions' and self.related_announcement:
            suggestions = self.related_announcement.get_suggestions_for_agent(self.agent)
            return suggestions.values('created_by').distinct().count()
        return 0


class DailyTaskStatus(models.Model):
    agent = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='daily_task_statuses', verbose_name='مشاور')
    date = models.CharField(max_length=10, verbose_name='تاریخ')
    report_done = models.BooleanField(default=False, verbose_name='گزارش ثبت شده')
    ads_done = models.BooleanField(default=False, verbose_name='انجام وظیفه آگهی')
    eva_done = models.BooleanField(default=False, verbose_name='انجام وظیفه کارشناسی')
    dis_done = models.BooleanField(default=False, verbose_name='انجام وظیفه تخفیف')
    ser_done = models.BooleanField(default=False, verbose_name='انجام وظیفه سرویس')
    report = models.OneToOneField(Report, on_delete=models.CASCADE, null=True, blank=True, related_name='daily_task_status',
                                  verbose_name='گزارش')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'وظایف (وضعیت)'
        verbose_name_plural = 'وظایف (وضعیت)'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['agent', 'date']),
        ]
        unique_together = [
            ('agent', 'date'),
        ]

    def __str__(self):
        return f"{self.agent} - {self.date}"

    def update_from_report(self, report):
        self.report = report
        self.report_done = True
        report_items = report.items.all()
        for item in report_items:
            if item.type == 'ads':
                self.ads_done = True
            elif item.type == 'eva':
                self.eva_done = True
            elif item.type == 'dis':
                self.dis_done = True
            elif item.type == 'ser':
                self.ser_done = True
        self.save()

    def is_friday(self):
        year, month, day = map(int, self.date.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        return jalali_date.weekday() == 4

    @classmethod
    def get_or_create_for_today(cls, agent):
        """Get or create daily task status for today"""
        today = jdatetime.date.today().strftime('%Y/%m/%d')

        # Check if Friday
        year, month, day = map(int, today.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        if jalali_date.weekday() == 4:  # Friday
            return None

        obj, created = cls.objects.get_or_create(
            agent=agent,
            date=today
        )
        return obj


# --------------------------------- Chat ---------------------------------
class ChatRoom(models.Model):
    room_type = models.CharField(max_length=10, choices=choices.room_types, verbose_name='نوع اتاق')
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    participants = models.ManyToManyField(CustomUserModel, related_name='chat_rooms', verbose_name='اعضا')
    created_by = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_rooms', verbose_name='ایجاد شده توسط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان بروزرسانی')

    class Meta:
        verbose_name = 'اتاق چت'
        verbose_name_plural = 'اتاق‌های چت'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['room_type', '-updated_at']),
        ]

    def __str__(self):
        if self.room_type == 'private':
            participants = self.participants.all()[:2]
            names = [p.name_family or p.username for p in participants]
            return f"چت: {' - '.join(names)}"
        return self.name or f"{self.get_room_type_display()}"

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_unread_count(self, user):
        return self.messages.exclude(
            read_by=user
        ).exclude(
            sender=user
        ).count()


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='اتاق')
    sender = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='فرستنده')
    message_type = models.CharField(max_length=10, choices=choices.message_types, default='text', verbose_name='نوع پیام')
    content = models.TextField(blank=True, null=True, verbose_name='محتوا')
    file = models.FileField(upload_to='chat_files/%Y/%m/%d/', blank=True, null=True, verbose_name='فایل')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies',
                                 verbose_name='پاسخ به')
    forwarded_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forwards',
                                       verbose_name='فوروارد از')
    read_by = models.ManyToManyField(CustomUserModel, blank=True, related_name='read_messages', verbose_name='خوانده شده توسط')
    is_edited = models.BooleanField(default=False, verbose_name='ویرایش شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ارسال')
    edited_at = models.DateTimeField(null=True, blank=True, verbose_name='زمان ویرایش')

    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.name_family or self.sender.username}: {self.content[:50] if self.content else self.message_type}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.room.save()

    def get_jalali_time(self):
        jalali_dt = jdatetime.datetime.fromgregorian(datetime=self.created_at)
        return jalali_dt.strftime('%H:%M')

    def get_jalali_date(self):
        jalali_dt = jdatetime.datetime.fromgregorian(datetime=self.created_at)
        return jalali_dt.strftime('%Y/%m/%d')


class MessageReaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions', verbose_name='پیام')
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='message_reactions', verbose_name='مشاور')
    emoji = models.CharField(max_length=10, verbose_name='اموجی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان')

    class Meta:
        verbose_name = 'واکنش پیام'
        verbose_name_plural = 'واکنش‌های پیام'
        unique_together = ['message', 'user', 'emoji']
        indexes = [
            models.Index(fields=['message', 'emoji']),
        ]

    def __str__(self):
        return f"{self.user.name_family or self.user.username} - {self.emoji}"



