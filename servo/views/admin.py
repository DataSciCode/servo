# coding=utf-8

import logging, hashlib
from datetime import datetime
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse

from bson.objectid import ObjectId
from servo.models import *

def settings(req):
    if len(Configuration.objects) < 1:
        config = Configuration()
    else:
        config = Configuration.objects.first()

    if req.method == "POST":

        for k, v in req.POST.items():
            config.__setattr__(k, v)

        config.imap_ssl = 'imap_ssl' in req.POST
        config.save()

        return HttpResponse('Asetukset tallennettu')
    else:
        return render(req, 'admin/settings.html', config)

def status(req):
    statuses = Status.objects
    return render(req, 'admin/status.html', {'statuses': statuses})

def status_form(req, id = None):
  status = Status()
  if id:
    status = Status.objects(id = ObjectId(id))[0]
    
  queues = Queue.objects
  factors = {'60': 'Minuuttia', '3600': 'Tuntia', '86400': 'Päivää', '604800': 'Viikkoa'}
  return render(req, 'admin/status_form.html', {'status': status, 'queues': queues, 'factors': factors})

def status_save(req):
    status = Status(title=req.POST['title'], description=req.POST['description'])
    status.save()

def gsx_accounts(req):
    accounts = GsxAccount.objects
    return render(req, 'admin/gsx_accounts.html', {'accounts': accounts })

def gsx_form(req, id = None):
  act = GsxAccount()
  
  if id:
    act = GsxAccount.objects(id = ObjectId(id)).first()
    
  envs = {'': 'Tuotanto', 'it': 'Kehitys', 'ut': 'Testaus'}
  return render(req, 'admin/gsx_form.html', {'account': act, 'environments': envs})

def gsx_save(req):
    act = GsxAccount()

    if 'id' in req.POST:
        act = GsxAccount.objects(id = req.POST['id']).first()

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
  
def users(req):
    users = User.objects.all()
    return render(req, 'admin/users.html', {'users': users})
  
def edit_user(req, id=None):
    print "lalalala"
    user = User()
    locations = Location.objects.all()

    if id:
        user = User.objects.get(id = id)
    
    return render(req, 'admin/user_form.html', {'user': user, 'locations': locations})

def locations(req):
    locations = Location.objects.all()
    return render(req, 'admin/locations.html', {'locations': locations})

def edit_location(req, id=None):
    location = Location()
  
    if id:
        location = Location.objects(id  = ObjectId(id)).first()
  
    return render(req, 'admin/location_form.html', {'location': location})

def save_location(req):
    loc = Location()

    if 'id' in req.POST:
        loc = Location.objects(id = ObjectId(req.POST['id'])).first()

    for k, v in req.POST.items():
        loc.__setattr__(k, v)

    loc.save()

    return HttpResponse('Sijainti tallennettu')
  
def save_user(req):
    user = User()

    if 'id' in req.POST:
        user = User.objects.get(id = req.POST['id'])
    else:
        user = User()

    if req.POST['password']:
        user.password = hashlib.sha1(req.POST['password']).hexdigest()

    user.username = req.POST.get('username')
    user.fullname = req.POST.get('fullname')
    user.email = req.POST.get('email')
    user.phone = req.POST.get('phone')
    user.locale = req.POST.get('locale')
    user.role = req.POST.get('role')
    user.location = Location.objects.get(id = req.POST.get('location'))
    user.save()

    return HttpResponse('Käyttäjä tallennettu')

def save_status(req):
    status = Status()
    if 'id' in req.POST:
        status = Status.objects(id = ObjectId(req.POST['id']))[0]
        status.title = req.POST['title']
        status.description = req.POST['description']
        status.limit_green = req.POST['limit_green']
        status.limit_yellow = req.POST['limit_yellow']
        status.limit_factor = req.POST['limit_factor']

        status.save()

    return HttpResponse('Status tallennettu')
