import logging
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render

from models import Order, Message

def index(req):
  return render(req, 'index.html', {"data" : Order.objects })

def issues(req):
  pass

def messages(req):
  messages = Message.objects
  return render(req, 'messages.html', {'messages' : messages })

def message_form(req):
  return render(req, 'message_form.html')

def message_save(req):
  m = Message(body="test", subject="Subject")
  m.save()
