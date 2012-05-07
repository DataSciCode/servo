# coding=utf-8
import logging, json
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime

from bson.objectid import ObjectId
from servo3.models import Order, Message, Template, Event, Queue, Tag, User

def index(req, param="", value=""):
  return render(req, 'orders/index.html', {'data' : Order.objects })
  
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
  queues = Queue.objects
  users = User.objects
  return render(req, 'orders/edit.html', {'order': o, 'queues': queues, 'users': users})

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
  