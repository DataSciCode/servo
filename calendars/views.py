from servo3.models import Calendar
from django.shortcuts import render
from django.http import HttpResponse

def index(req):
  """docstring for index"""
  calendars = Calendar.objects()
  return render('calendars/index.html')
  