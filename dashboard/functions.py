from jdatetime import date, timedelta, datetime
from jalali_date import datetime2jalali
from django.utils import timezone


def current_month():
    now = timezone.now()
    today = datetime2jalali(now)
    past_days = []
    for i in range(0, 31):
        past_day = today - timedelta(days=i)
        if past_day.month == today.month:
            past_day = past_day.strftime('%Y/%m/%d')
            past_days.append(past_day)
    future_days = []
    for i in range(1, 31):
        next_day = today + timedelta(days=i)
        if next_day.month == today.month:
            next_day = next_day.strftime('%Y/%m/%d')
            future_days.append(next_day)
    return sorted(past_days + future_days, key=lambda x: int(x.split('/')[2]))


def previous_month():
    now = timezone.now()
    today = datetime2jalali(now)
    first_day_current = today.replace(day=1)
    last_day_previous = first_day_current - timedelta(days=1)
    first_day_previous = last_day_previous.replace(day=1)
    days_list = []
    this_day = first_day_previous
    while this_day.month == last_day_previous.month:
        days_list.append(this_day.strftime('%Y/%m/%d'))
        this_day += timedelta(days=1)
    return days_list


def previous_2_month():
    now = timezone.now()
    today = datetime2jalali(now)
    target_month = today.month - 2
    target_year = today.year
    if target_month <= 0:
        target_month += 12
        target_year -= 1
    first_day_target = today.replace(year=target_year, month=target_month, day=1)
    days_list = []
    this_day = first_day_target
    while this_day.month == target_month:
        days_list.append(this_day.strftime('%Y/%m/%d'))
        this_day += timedelta(days=1)
    return days_list


def next_month():
    now = timezone.now()
    today = datetime2jalali(now)
    target_month = today.month + 1
    target_year = today.year
    if target_month > 12:
        target_month = 1
        target_year += 1
    first_day_next = today.replace(year=target_year, month=target_month, day=1)
    days_list = []
    this_day = first_day_next
    while this_day.month == target_month:
        days_list.append(this_day.strftime('%Y/%m/%d'))
        this_day += timedelta(days=1)
    return days_list


def next_2_month():
    now = timezone.now()
    today = datetime2jalali(now)
    target_month = today.month + 2
    target_year = today.year
    if target_month > 12:
        target_month -= 12
        target_year += 1
    first_day_target = today.replace(year=target_year, month=target_month, day=1)
    days_list = []
    this_day = first_day_target
    while this_day.month == target_month:
        days_list.append(this_day.strftime('%Y/%m/%d'))
        this_day += timedelta(days=1)
    return days_list


def current_month_finder(number):
    number = str(number)
    if number == '1':
        return 'فروردین'
    if number == '2':
        return 'اردیبهشت'
    if number == '3':
        return 'خرداد'
    if number == '4':
        return 'تیر'
    if number == '5':
        return 'مرداد'
    if number == '6':
        return 'شهریور'
    if number == '7':
        return 'مهر'
    if number == '8':
        return 'آبان'
    if number == '9':
        return 'آذر'
    if number == '10':
        return 'دی'
    if number == '11':
        return 'بهمن'
    if number == '12':
        return 'اسفند'


def previous_month_finder(number):
    number = str(number)
    if number == '1':
        return 'اسفند'
    if number == '2':
        return 'فروردین'
    if number == '3':
        return 'اردیبهشت'
    if number == '4':
        return 'خرداد'
    if number == '5':
        return 'تیر'
    if number == '6':
        return 'مرداد'
    if number == '7':
        return 'شهریور'
    if number == '8':
        return 'مهر'
    if number == '9':
        return 'آبان'
    if number == '10':
        return 'آذر'
    if number == '11':
        return 'دی'
    if number == '12':
        return 'بهمن'


def previous_2_month_finder(number):
    number = str(number)
    if number == '1':
        return 'بهمن'
    if number == '2':
        return 'اسفند'
    if number == '3':
        return 'فروردین'
    if number == '4':
        return 'اردیبهشت'
    if number == '5':
        return 'خرداد'
    if number == '6':
        return 'تیر'
    if number == '7':
        return 'مرداد'
    if number == '8':
        return 'شهریور'
    if number == '9':
        return 'مهر'
    if number == '10':
        return 'آبان'
    if number == '11':
        return 'آذر'
    if number == '12':
        return 'دی'


def next_month_finder(number):
    number = str(number)
    if number == '1':
        return 'اردیبهشت'
    if number == '2':
        return 'خرداد'
    if number == '3':
        return 'تیر'
    if number == '4':
        return 'مرداد'
    if number == '5':
        return 'شهریور'
    if number == '6':
        return 'مهر'
    if number == '7':
        return 'آبان'
    if number == '8':
        return 'آذر'
    if number == '9':
        return 'دی'
    if number == '10':
        return 'بهمن'
    if number == '11':
        return 'اسفند'
    if number == '12':
        return 'فروردین'


def next_2_month_finder(number):
    number = str(number)
    if number == '1':
        return 'خرداد'
    if number == '2':
        return 'تیر'
    if number == '3':
        return 'مرداد'
    if number == '4':
        return 'شهریور'
    if number == '5':
        return 'مهر'
    if number == '6':
        return 'آبان'
    if number == '7':
        return 'آذر'
    if number == '8':
        return 'دی'
    if number == '9':
        return 'بهمن'
    if number == '10':
        return 'اسفند'
    if number == '11':
        return 'فروردین'
    if number == '12':
        return 'اردیبهشت'


