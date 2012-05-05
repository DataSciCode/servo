# coding=utf-8

from django import template
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
