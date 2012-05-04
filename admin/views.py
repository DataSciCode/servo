# coding=utf-8

import logging
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from django.http import HttpResponse

from servo3.models import Status, Queue, GsxAccount, Field
from pymongo.objectid import ObjectId

def status(req):
  statuses = Status.objects
  return render(req, 'status.html', statuses)

def status_form(req):
  status = Status()
  return render(req, 'status_form.html', status)

def status_save(req):
  status = Status(title=req.POST['title'], description=req.POST['description'])
  status.save()

def queues(req):
  queues = Queue.objects
  return render(req, 'queues.html', queues)

def queue_form(req):
  return render(req, 'queue_form.html')

def gsx_accounts(req):
  return render(req, 'gsx_accounts.html')

def gsx_form(req):
  act = GsxAccount()
  return render(req, 'gsx_form.html', act)

def gsx_save(req):
  pass

def gsx_remove(req):
  pass

def fields(req):
  return render(req, 'fields.html', {'fields' : Field.objects})

def edit_field(req, id=None):
  field = Field()
  if(id):
    field = Field.objects(id=ObjectId(id))[0]
  return render(req, 'field_form.html', field)

def save_field(req):
  if(req.POST['id']):
    field = Field(id=ObjectId(req.POST['id']))
  else:
    field = Field()
  
  field.title = req.POST['title']
  field.type = req.POST['type']
  field.format = req.POST['format']
  field.save()
  
  return HttpResponse("Kenttä tallennettu")

def remove_field(req, id=None):
  if 'id' in req.POST:
    field = Field(id=ObjectId(req.POST['id']))
    field.delete()
    return HttpResponse("Kenttä poistettu")
  else:
    field = Field.objects(id=ObjectId(id))[0]
    return render(req, 'field_remove.html', field)
