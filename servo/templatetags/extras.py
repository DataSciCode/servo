# coding=utf-8

import re, json, datetime
from django import template
from django.utils import safestring, timezone

register = template.Library()

@register.filter
def relative_date(value):
    result = ""

    if type(value) != datetime.datetime:
        return result

    #result = value.date()
    today = timezone.now()
    delta =  today - value

    if delta <= datetime.timedelta(hours=8):
        print delta
        result = 'Tänään klo %s' % value.strftime("%k:%M")

    if delta > datetime.timedelta(hours=8):
        result = 'Eilen klo %s' % value.strftime("%k:%M")

    if delta > datetime.timedelta(days=2):
        result = value.strftime("%a, %d.%m.%y klo %k:%M")

    return result
  
@register.filter
def clickable(value):
    result = value
    if re.search('^[\w\.\-_]+@[\w\.\-_]+\.[a-z]{2,4}$', value):
        result = '<a href="/message/mailto/%s" class="popup">%s</a>' % (value, value)
    if re.search('^\+?\d{8}', value):
        result = '<a href="/message/smsto/%s" class="popup">%s</a>' % (value, value)

    return safestring.mark_safe(result)

@register.filter
def gsx_date(value):
    formats = json.load(open("/Users/filipp/Projects/servo3/gsxlib/langs.json"))
    return value.strftime(formats['en_XXX']['df'])
  
@register.filter
def gsx_time(value):
    formats = json.load(open("/Users/filipp/Projects/servo3/gsxlib/langs.json"))
    return value.strftime(formats['en_XXX']['tf'])
