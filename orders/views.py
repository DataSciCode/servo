import logging
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime

from pymongo.objectid import ObjectId

from servo3.models import Order, Message

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
  return render(req, 'message_form.html', {'message' : m})

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
#  m = Message.objects(order__number = o.number)
  return render(req, 'edit.html', {'order': o, 'title': 'Tilaus #asd'})
