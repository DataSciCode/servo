# coding=utf-8
import logging
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime

from pymongo.objectid import ObjectId

from servo3.models import Order, Message, Template

def index(req, param="", value=""):
  return render(req, 'index.html', {"data" : Order.objects })

def issues(req):
  pass

def messages(req):
  messages = Message.objects
  return render(req, 'messages.html', {'messages' : messages })

def message_form(req, order_id=None):
  m = Message()
  m.order_id = order_id
  return render(req, 'message_form.html', {'message' : m, 'templates': Template.objects})

def message_save(req):
  m = Message(created_by = 'filipp')
  m.subject = req.POST['body']
  m.body = req.POST['body']
  m.smsto = req.POST['smsto']
  m.mailto = req.POST['mailto']
  
  if(req.POST['order']):
    order = Order.objects(id=ObjectId(req.POST['order']))[0]
    m.order = order
  m.save()
  
  return HttpResponse('Viesti tallennettu')

def issue_create(req):
  pass

def message_view(req, id):
  m = Message.objects(id=ObjectId(id))[0]
  return render(req, "message_view.html", m)
  
def create(req):
  o = Order(created_by = "filipp", created_at = datetime.now())
  o.save()
  return redirect('/orders/edit/' + str(o.id))

def edit(req, id):
  o = Order.objects(id=ObjectId(id))[0]
  return render(req, 'edit.html', {'order': o, 'title': 'Tilaus #asd'})

def remove(req, id=None):
  """docstring for remove"""
  if 'id' in req.POST:
    order = Order.objects(id = ObjectId(req.POST['id']))
    order.delete()
    return HttpResponse('Tilaus poistettu')
  else :
    order = Order.objects(id = ObjectId(id))[0]
    return render(req, 'remove.html', order)

def remove_message(req, id=None):
  """docstring for remove_message"""
  if 'id' in req.POST:
    msg = Message.objects(id = ObjectId(req.POST['id']))
    msg.delete()
    return HttpResponse('Viesti poistettu')
  else:
    msg = Message.objects(id = ObjectId(id))[0]
    return render(req, 'remove_message.html', msg)
