import os
import zipfile

import random
import string
from jdatetime import date, timedelta, datetime
# from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext as _

from . import choices


# -------------------------------- CODES ----------------------------------
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_unique_code():
    return ''.join(random.choices(string.digits + string.digits, k=6))


# -------------------------------- TIMES ----------------------------------
def next_week_shamsi():
    days = []
    today = datetime.today()
    for i in range(1, 8):
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
        label = f"{weekday_fa} - {date_str}"
        days.append((date_str, label))
    return days


def next_month_shamsi():
    days = []
    today = datetime.today()
    for i in range(1, 31):
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
        label = f"{weekday_fa} - {date_str}"
        days.append((date_str, label))
    return days


def last_month_shamsi():
    days = []
    today = datetime.today()
    for i in range(1, 31):
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
        label = f"{weekday_fa} - {date_str}"
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
    ]
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, null=True, verbose_name=_('Title'))
    sub_district = models.ForeignKey(SubDistrict, on_delete=models.SET_NULL, null=True, blank=True, related_name='agents', verbose_name=_('Sub-District'))
    email = models.EmailField(unique=False, blank=True, null=True)
    REQUIRED_FIELDS = []

    @property
    def is_boss(self):
        if self.title == 'bs':
            return choices.beings[0]
        else:
            return choices.beings[1]


# --------------------------------- FILE -----------------------------------
class Person(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=150, blank=True, null=True, verbose_name=_('Description'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))

    class Meta:
        verbose_name = 'شخص آگهی‌دهنده'
        verbose_name_plural = 'اشخاص آگهی‌دهنده'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('person_detail', args=[self.pk])


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
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)

    @property
    def price_per_meter(self):
        return int(self.price_announced/self.area)

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

    def zip_file_admin(self):
        zip_url = self.zip_file
        if zip_url:
            return format_html('<a href="{}" download>Download ZIP</a>', zip_url)
        return "No media"

    zip_file_admin.short_description = "Download ZIP"

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
    unique_url_id = models.CharField(max_length=20, null=True, unique=True, blank=True)
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_expired = models.DateTimeField(blank=True, null=True)

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

    def zip_file_admin(self):
        zip_url = self.zip_file
        if zip_url:
            return format_html('<a href="{}" download>Download ZIP</a>', zip_url)
        return "No media"

    zip_file_admin.short_description = "Download ZIP"

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
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers', verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers', verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='buyers', verbose_name=_('District'))
    sub_districts = models.ManyToManyField(SubDistrict, blank=True, related_name='buyers', verbose_name=_('Sub-Districts'))
    # properties
    budget_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Budget'))
    budget_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Budget'))
    budget_status = models.CharField(max_length=15, choices=choices.budgets, blank=True, null=True, verbose_name=_('Budget Status'))
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
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Description'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
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
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters', verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters', verbose_name=_('City'))
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='renters', verbose_name=_('District'))
    sub_districts = models.ManyToManyField(SubDistrict, blank=True, related_name='renters', verbose_name=_('Sub-Districts'))
    # properties
    deposit_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Deposit'))
    deposit_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Deposit'))
    rent_announced = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Announced Rent'))
    rent_max = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Max Rent'))
    budget_status = models.CharField(max_length=15, choices=choices.budgets, blank=True, null=True, verbose_name=_('Budget Status'))
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
    phone_number = models.CharField(max_length=11, unique=True, verbose_name=_('Phone Number'))
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name=_('Description'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.statuses, default='pen', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date and Time of Creation'))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
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
class Visit(models.Model):
    sale_file_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Sale File Code'))
    rent_file_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Rent File Code'))
    buyer_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Buyer Code'))
    renter_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Renter Code'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    date = models.CharField(max_length=200, verbose_name=_('Date of Visit'))
    time = models.CharField(max_length=200, choices=choices.times, verbose_name=_('Time of Visit'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.serv_statuses, default='sub', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sale_file(self):
        if self.sale_file_code:
            file = SaleFile.objects.filter(code=self.sale_file_code)
            return file

    @property
    def rent_file(self):
        if self.rent_file_code:
            file = RentFile.objects.filter(code=self.rent_file_code)
            return file

    @property
    def buyer(self):
        if self.buyer_code:
            buyer = Buyer.objects.filter(code=self.buyer_code)
            return buyer

    @property
    def renter(self):
        if self.renter_code:
            renter = Renter.objects.filter(code=self.renter_code)
            return renter

    def save(self, *args, **kwargs):
        if self.sale_file_code:
            self.type = choices.types[0]
        if self.rent_file_code:
            self.type = choices.types[1]
        if not self.code:
            self.code = generate_unique_code()
        super(Visit, self).save(*args, **kwargs)

    def __str__(self):
        return f'بازدید: {self.type} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'بازدید'
        verbose_name_plural = 'بازدیدها'

    def get_absolute_url(self):
        return reverse('visit_detail', args=[self.pk, self.code])


class Session(models.Model):
    sale_file_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Sale File Code'))
    rent_file_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Rent File Code'))
    buyer_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Buyer Code'))
    renter_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Renter Code'))
    visit_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Visit Code'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    date = models.CharField(max_length=200, verbose_name=_('Date of Visit'))
    time = models.CharField(max_length=200, choices=choices.times, verbose_name=_('Time of Visit'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    status = models.CharField(max_length=10, choices=choices.serv_statuses, default='sub', verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sale_file(self):
        if self.sale_file_code:
            file = SaleFile.objects.filter(code=self.sale_file_code)
            return file

    @property
    def rent_file(self):
        if self.rent_file_code:
            file = RentFile.objects.filter(code=self.rent_file_code)
            return file

    @property
    def buyer(self):
        if self.buyer_code:
            buyer = Buyer.objects.filter(code=self.buyer_code)
            return buyer

    @property
    def renter(self):
        if self.renter_code:
            renter = Renter.objects.filter(code=self.renter_code)
            return renter

    @property
    def visit(self):
        visit = Visit.objects.filter(code=self.visit_code)
        return visit

    def save(self, *args, **kwargs):
        self.type = self.visit.type
        if not self.code:
            self.code = generate_unique_code()
        super(Session, self).save(*args, **kwargs)

    def __str__(self):
        return f'نشست: {self.type} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'نشست'
        verbose_name_plural = 'نشست‌ها'

    def get_absolute_url(self):
        return reverse('session_detail', args=[self.pk, self.code])


class Trade(models.Model):
    session_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Session Code'))
    type = models.CharField(max_length=10, verbose_name=_('Type of Trade'))
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    date = models.CharField(max_length=200, verbose_name=_('Date of Trade'))
    price = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Price'))
    deposit = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Deposit'))
    rent = models.PositiveBigIntegerField(blank=True, null=True, verbose_name=_('Rent'))
    contract_owner = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Contract Owner (Seller / Lessor)'))
    contract_buyer = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Contract Customer (Buyer)'))
    contract_renter = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Contract Customer (Renter)'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Code'))
    followup_code = models.CharField(max_length=6, null=True, unique=True, blank=True, verbose_name=_('Followup Code'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sale_file(self):
        if self.type == 'sale':
            file = self.session.sale_file
            return file

    @property
    def rent_file(self):
        if self.type == 'rent':
            file = self.session.rent_file
            return file

    @property
    def buyer(self):
        if self.type == 'sale':
            buyer = self.session.buyer
            return buyer

    @property
    def renter(self):
        if self.type == 'rent':
            renter = self.session.renter
            return renter

    @property
    def owner(self):
        if self.type == 'sale':
            if self.session.sale_file.source == 'PN':
                owner = self.session.sale_file.source
                return owner
        if self.type == 'rent':
            if self.session.rent_file.source == 'PN':
                owner = self.session.rent_file.source
                return owner

    @property
    def session(self):
        session = Session.objects.filter(code=self.session_code)
        return session

    def save(self, *args, **kwargs):
        self.type = self.session.type
        if not self.code:
            self.code = generate_unique_code()
        super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        return f'معامله: {self.type} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'معامله'
        verbose_name_plural = 'معاملات'

    def get_absolute_url(self):
        return reverse('trade_detail', args=[self.pk, self.code])


# --------------------------------- MNGs ---------------------------------
class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    deadline = models.CharField(max_length=200, verbose_name=_('Deadline'))
    type = models.CharField(max_length=10, choices=choices.task_types,  verbose_name=_('Type of Task'))
    agent = models.ForeignKey(CustomUserModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Agent'))
    sale_file = models.ForeignKey(SaleFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Sale File'))
    rent_file = models.ForeignKey(RentFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Rent File'))
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Buyer'))
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name=_('Renter'))
    code = models.CharField(max_length=6, null=True, unique=True, blank=True)
    description = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Description'))
    result = models.TextField(max_length=1000, blank=True, null=True, verbose_name=_('Result'))
    status = models.CharField(max_length=10, choices=choices.task_statuses, default='OP',  verbose_name=_('Status'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date and Time of Creation'))

    @property
    def sub_district(self):
        return self.agent.sub_district

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_unique_code()
        super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.type} / {self.code}'

    class Meta:
        ordering = ('-datetime_created',)
        verbose_name = 'وظیفه'
        verbose_name_plural = 'وظایف'

    def get_absolute_url(self):
        return reverse('task_detail', args=[self.pk, self.code])



