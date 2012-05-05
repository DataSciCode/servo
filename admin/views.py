# coding=utf-8

import logging
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from django.http import HttpResponse

from servo3.models import Status, Queue, GsxAccount, Field, Template
from pymongo.objectid import ObjectId

def status(req):
  statuses = Status.objects
  return render(req, 'admin/status.html', statuses)

def status_form(req):
  status = Status()
  return render(req, 'admin/status_form.html', status)

def status_save(req):
  status = Status(title=req.POST['title'], description=req.POST['description'])
  status.save()

def queues(req):
  queues = Queue.objects
  return render(req, 'admin/queues.html', queues)

def queue_form(req):
  return render(req, 'admin/queue_form.html')

def gsx_accounts(req):
  return render(req, 'admin/gsx_accounts.html')

def gsx_form(req):
  act = GsxAccount()
  return render(req, 'admin/gsx_form.html', act)

def gsx_save(req):
  pass

def gsx_remove(req):
  pass

def fields(req):
  return render(req, 'admin/fields.html', {'fields' : Field.objects})

def edit_field(req, id=None):
  field = Field()
  if(id):
    field = Field.objects(id=ObjectId(id))[0]
  return render(req, 'admin/field_form.html', field)

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
    return render(req, 'admin/field_remove.html', field)

def templates(req):
  return render(req, 'admin/templates.html', {'templates': Template.objects})

def create_template(req):
  return render(req, 'admin/template_form.html')

def save_template(req):
  template = Template()
  
  if 'id' in req.POST:
    template = Template.objects(id = ObjectId(req.POST['id']))[0]
  
  template.title = req.POST['title']
  template.body = req.POST['body']
  template.save()
  
  return HttpResponse('Pohja tallennettu')

def view_template(req, id):
  t = Template.objects(id = ObjectId(id))[0]
  return HttpResponse(t.body)
