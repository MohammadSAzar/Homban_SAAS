from django import template


register = template.Library()


@register.filter
def price_converter(price):
    if int(price):
        if int(price) / 1000000 >= 1:
            return price
        else:
            return int(price) * 1000000


