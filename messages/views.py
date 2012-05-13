from bson.objectid import ObjectId
from django.shortcuts import render
from django.http import HttpResponse

from servo3.models import Message, Template, Order, Attachment

def index(req):
  messages = Message.objects
  return render(req, 'messages/index.html', {'messages' : messages })
  
def form(req, order_id = None):
  m = Message()
  m.order_id = order_id
  return render(req, 'messages/form.html', {'message' : m,\
    'templates': Template.objects})
  
def edit(req, id = None):
  m = Message.objects(id = ObjectId(id)).first()
  return render(req, 'messages/form.html', {'message' : m,\
    'templates': Template.objects})
  
def reply(req, id):
  parent = Message.objects(id = ObjectId(id)).first()
  m = Message(path = parent.path)
  return render(req, 'messages/form.html', {'message' : m,\
    'templates': Template.objects})
  
def save(req):
  m = Message(sender="filipp")
  m.body = req.POST.get("body")
  m.smsto = req.POST.get("smsto")
  m.subject = req.POST.get("body")
  m.mailto = req.POST.get("mailto")
  
  for a in req.POST.getlist("attachments"):
    doc = Attachment.objects(id = ObjectId(a)).first()
    m.attachments.append(doc)
  
  if 'order' in req.POST:
    order = Order.objects(id=ObjectId(req.POST['order'])).first()
    m.order = order
  
  if(m.mailto):
    m.send_mail()
  
  if(m.smsto):
    m.send_sms()
  
  m.save()
  
  return HttpResponse('Viesti tallennettu')

def remove(req, id=None):
  if 'id' in req.POST:
    msg = Message.objects(id = ObjectId(req.POST['id']))
    msg.delete()
    return HttpResponse('Viesti poistettu')
  else:
    msg = Message.objects(id = ObjectId(id))[0]
    return render(req, 'messages/remove.html', msg)
    
def view(req, id):
  m = Message.objects(id = ObjectId(id))[0]
  return render(req, 'messages/view.html', m)
  