from django import template

register = template.Library()


@register.filter
def farsi_number(number):
    number = str(number)
    converted_number = number.maketrans('1234567890', '۱۲۳۴۵۶۷۸۹۰')
    return number.translate(converted_number)

