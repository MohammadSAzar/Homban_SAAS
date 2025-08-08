from django import template
import jdatetime


register = template.Library()


@register.filter
def weekday_finder(day):
    try:
        if hasattr(day, 'strftime'):
            date_obj = day
        else:
            year, month, day_num = map(int, day.split('/'))
            date_obj = jdatetime.date(year, month, day_num)
        weekday_en = date_obj.strftime('%A')
        weekday_map = {
            'Monday': 'دوشنبه',
            'Tuesday': 'سه‌شنبه',
            'Wednesday': 'چهارشنبه',
            'Thursday': 'پنج‌شنبه',
            'Friday': 'جمعه',
            'Saturday': 'شنبه',
            'Sunday': 'یکشنبه'
        }
        return weekday_map.get(weekday_en, 'نامشخص')
    except:
        return 'نامشخص'


