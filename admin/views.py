# coding=utf-8

import logging
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime
from django.http import HttpResponse

from servo3.models import Status, Queue, GsxAccount, Field, Template, Config
from bson.objectid import ObjectId

def settings(req):
  
  if len(Config.objects) < 1:
    config = Config()
  else:
    config = Config.objects[0]
  
  if len(req.POST) > 0:
    
    config.imap_host = req.POST['imap_host']
    config.imap_user = req.POST['imap_user']
    config.imap_ssl = 'imap_ssl' in req.POST
    config.imap_password = req.POST['imap_password']
    config.smtp_host = req.POST['smtp_host']
    
    config.sms_url = req.POST['sms_url']
    config.sms_user = req.POST['sms_user']
    config.sms_password = req.POST['sms_password']
    
    config.save()
    
    return HttpResponse('Asetukset tallennettu')
  else:
    return render(req, 'admin/settings.html', config)
  
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
  return render(req, 'admin/queues.html', {'queues': queues})

def queue_form(req, id=None):
  accounts = GsxAccount.objects
  queue = Queue()
  if id:
    queue = Queue.objects(id = ObjectId(id))[0]
  
  return render(req, 'admin/queue_form.html', {'queue' : queue, 'accounts' : accounts})

def queue_save(req):
  q = Queue()
  
  if 'id' in req.POST:
    q = Queue.objects(id = ObjectId(req.POST['id']))[0]
  
  q.title = req.POST['title']
  q.description = req.POST['description']
  q.gsx_account = GsxAccount.objects(id = ObjectId(req.POST['gsx_account']))[0]
  q.save()
  return HttpResponse('Jono tallennettu')

def gsx_accounts(req):
  accounts = GsxAccount.objects
  return render(req, 'admin/gsx_accounts.html', {'accounts': accounts })

def gsx_form(req):
  act = GsxAccount()
  envs = {'': 'Tuotanto', 'it': 'Kehitys', 'ut': 'Testaus'}
  return render(req, 'admin/gsx_form.html', {'account': act, 'environments': envs})

def gsx_save(req):
  act = GsxAccount()
  
  if 'id' in req.POST:
    act = GsxAccount.objects(id = req.POST['id'])[0]
    
  act.title = req.POST['title']
  act.sold_to = req.POST['sold_to']
  act.ship_to = req.POST['ship_to']
  act.username = req.POST['username']
  act.password = req.POST['password']
  act.environment = req.POST['environment']
  act.is_default = 'default' in req.POST
  act.save()
  
  return HttpResponse('GSX tili tallennettu')

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
