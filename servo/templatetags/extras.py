# coding=utf-8
import re, json, datetime
from django import template
from django.utils import safestring, timezone
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
def relative_date(value):
    result = ""
    if type(value) != datetime.datetime:
        return result

    current = timezone.now()
    delta =  current - value

    if delta <= datetime.timedelta(minutes=3):
        result = 'Hetki sitten'
    elif current.day == value.day:
        result = 'Tänään klo %s' % value.strftime("%k:%M")
    else:
        result = 'Eilen klo %s' % value.strftime("%k:%M")

    if delta > datetime.timedelta(days=2):
        result = value.strftime("%a, %d.%m.%y klo %k:%M")

    return result
  
@register.filter
def clickable(value, order=None):
    result = value
    if not isinstance(value, basestring):
        return ""
        
    if re.search('^[\w\.\-_]+@[\w\.\-_]+\.[a-z]{2,4}$', value):
        if order:
            result = '<a href="/orders/%d/mailto/%s" title="%s">%s...</a>' % (order, value, value, value[:25])
        else:
            result = '<a href="/notes/mailto/%s" title="%s">%s...</a>' % (value, value, value[:25])
    if re.search('^\+?\d{8}', value):
        if order:
            result = '<a href="/orders/%d/smsto/%s" title="%s">%s</a>' % (order, value, value, value)
        else:
            result = '<a href="/notes/smsto/%s" title="%s">%s</a>' % (value, value, value)

    return safestring.mark_safe(result)

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
