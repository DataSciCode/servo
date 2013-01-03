# coding=utf-8
import re, json, datetime
from django import template
from django.utils import safestring, timezone
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
def relative_date(value):
    result = ''
    if not isinstance(value, datetime.datetime):
        return result

    current = timezone.now()
    delta =  current - value
    time_format = {'time': value.strftime('%k:%M')}

    if delta <= datetime.timedelta(minutes=3):
        result = _(u'Hetki sitten')
    elif current.day == value.day:
        result = _(u'Tänään klo %(time)s') % time_format
    else:
        result = _(u'Eilen klo %(time)s') % time_format

    if delta > datetime.timedelta(days=2):
        result = value.strftime(_('%a, %d.%m klo %k:%M'))
    
    return result

@register.filter
def highlight(text, string):
    result = re.sub(r'('+string+')', '<span class="highlight">\g<0></span>', text)
    return safestring.mark_safe(result)

@register.filter
def price(value):
    try:
        return float(value)+10
    except ValueError:
        return value
