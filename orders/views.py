# coding=utf-8
import logging, json
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime

from bson.objectid import ObjectId
from servo3.models import Order, Message, Template, Event, Queue, Tag, User, Status, User

def index(req, param = None, value = None):
  data = Order.objects
  
  if param == "status":
    status = Status.objects(id = ObjectId(value)).first()
    data = Order.objects(status = status)
  
  if param == "user":
    user = User.objects(username = value).first()
    data = Order.objects(user = user)
    
  return render(req, 'orders/index.html', {'data' : data})
  
def create(req):
  o = Order(created_by = "filipp", created_at = datetime.now())
  o.save()
  # fire the event
  e = Event(description = 'Tilaus luotu', ref_order = o, type = 'create_order')
  e.save()
  
  return redirect('/orders/edit/' + str(o.id))
  
def tags(req, id):
  if 'title' in req.POST:
    order = Order.objects(id = ObjectId(id))[0]
    title = req.POST['title']
    
    if title not in order.tags:
      order.tags.append(title)
      order.save()
    
    if len(Tag.objects(title = title, type = 'order')) < 1:
      tag = Tag(title = title, type = 'order')
      tag.save()
    
    return HttpResponse(json.dumps({order.tags}), content_type='application/json')
  
def edit(req, id):
  o = Order.objects(id=ObjectId(id)).first()
  req.session['order'] = o
  queues = Queue.objects
  users = User.objects
  statuses = Status.objects
  priorities = ['Matala', 'Normaali', 'Korkea']
  return render(req, 'orders/edit.html', {'order': o, 'queues': queues,\
    'users': users, 'statuses': statuses, 'priorities': priorities})

def remove(req, id=None):
  """docstring for remove"""
  if 'id' in req.POST:
    order = Order.objects(id = ObjectId(req.POST['id']))
    order.delete()
    return HttpResponse('Tilaus poistettu')
  else :
    order = Order.objects(id = ObjectId(id))[0]
    return render(req, 'orders/remove.html', order)
    
def follow(req, id):
  order = Order.objects(id = ObjectId(id))[0]
  if 'filipp' not in order.followers:
    order.followers.append('filipp')
    order.save()
  
  return HttpResponse('%d seuraa' % len(order.followers))
  
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update(req, id):
  if 'queue' in req.POST:
    queue = ObjectId(req.POST['queue'])
    queue = Queue.objects(id = queue).first()
    req.session['order'].queue = queue
    req.session['order'].save()
    event = Event(description = queue.title, ref_order = req.session['order'], type = "set_queue")
    event.save()
  
  if 'status' in req.POST:
    from time import time
    status = ObjectId(req.POST['status'])
    status = Status.objects(id = status).first()
    # calculate when this status will timeout
    green = (status.limit_green*status.limit_factor)+time()
    yellow = (status.limit_yellow*status.limit_factor)+time()
    req.session['order'].status_limit_green = green
    req.session['order'].status_limit_yellow = yellow
    req.session['order'].status = status
    req.session['order'].save()
    event = Event(description = status.title, ref_order = req.session['order'], type = "set_status")
    event.save()
    
  if 'user' in req.POST:
    user = req.POST['user']
    user = User.objects(id = ObjectId(user)).first()
    req.session['order'].user = user
    req.session['order'].save()
    event = Event(description = user.fullname, ref_order = req.session['order'], type = "set_user")
    event.save()
    
  if 'priority' in req.POST:
    req.session['order'].priority = req.POST['priority']
    req.session['order'].save()
    
  return HttpResponse()
  