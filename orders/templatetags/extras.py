# coding=utf-8

import re
from django import template
from django.utils import safestring
import datetime

register = template.Library()

@register.filter
def relative_date(value):
  result = ''
  
  if type(value) != datetime.datetime:
    return result
    
  today = datetime.datetime.today()
  delta = value - today
  
  if delta < datetime.timedelta(days=1):
    result = 'Tänään klo %s' % value.time()
  elif delta == datetime.timedelta(days=2):
    result = 'Eilen klo %s' % value.time()
  else:
    result = value.date()
    
  return result
  
@register.filter
def clickable(value):
  
  result = value
  
  if re.search('^[\w\.\-_]+@[\w\.\-_]+\.[a-z]{2,4}$', value):
    result = '<a href="/message/create/mailto/%s">%s</a>' % (value, value)
  if re.search('^\+?\d{8}', value):
    result = '<a href="/message/create/smsto/%s">%s</a>' % (value, value)
  
  return safestring.mark_safe(result)
  