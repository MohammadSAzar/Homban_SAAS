from django import template
from jalali_date import datetime2jalali

register = template.Library()


@register.filter
def jalali_date_converter(a_date):
    return datetime2jalali(a_date).strftime('%Y/%m/%d')


