# coding=utf-8
import logging, json, re
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.datastructures import DotExpandedDict

from datetime import datetime

from bson.objectid import ObjectId
from django.views.decorators.csrf import csrf_exempt
from servo3.models import *

def index(req, param = None, value = None):
  data = Order.objects
  if param == "status":
    status = Status.objects(id = ObjectId(value)).first()
    data = Order.objects(status = status)
  
  if param == "user":
    user = User.objects(username = value).first()
    data = Order.objects(user = user)
  
  if param == "customer":
    customer = Customer.objects(id = ObjectId(value)).first()
    data = Order.objects(customer = customer)
    
  return render(req, 'orders/index.html', {'data' : data})
  
def create(req):
  o = Order(created_by = "filipp", created_at = datetime.now())
  o.save()
  # fire the creation event
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

@csrf_exempt
def update(req, id):
  order = Order.objects(id = ObjectId(id)).first()
  if 'queue' in req.POST:
    queue = ObjectId(req.POST['queue'])
    queue = Queue.objects(id = queue).first()
    order.queue = queue
    order.save()
    event = Event(description = queue.title, ref_order = order, type = "set_queue")
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
    
  return HttpResponse("")
  
def create_gsx_repair(req, order_id):
  
  order = Order.objects(id = ObjectId(order_id)).first()
  customer = {}
  templates = Template.objects.all()
  comptia = json.load(open("/Users/filipp/Projects/servo3/gsx/symptoms.json"))
  
  if order.customer:
    for k, v in order.customer.properties.items():
      if re.search('@', v):
        customer['emailAddress'] = v
      if re.search('\d+', v):
        customer['primaryPhone'] = v
  
  (customer['firstName'], customer['lastName']) = order.customer.name.split(" ")
  
  parts = []
  
  for p in order.products:
    # find the corresponding compnent code from coptia
    comp = p.product.gsx_data['componentCode']
    symptoms = comptia['symptoms'][comp]
    parts.append({"number": p.product.number,
      "title": p.product.title, "code": p.product.code, "symptoms": symptoms})
  
  return render(req, "orders/gsx_repair_form.html", {"templates": templates,\
    "parts": parts, "modifiers": comptia['modifiers'],\
    "customer": customer, "order": order})
    
def submit_gsx_repair(req):
  data = DotExpandedDict(req.POST)
  parts = []
  
  # create Purchase Order
  po = PurchaseOrder(supplier = "Apple", reference = data.get("order_number"))
  po.save()
  
  for k, v in data.get("items").items():
    # add to "ordered" inventory
    p = Product.objects(code = v['partNumber']).first()
    Inventory(kind = "po", product = p, slot = po).save()
    parts.append(v)
    
  po.products = parts
  po.carrier = "UPS"
  print parts
  po.save()
  
  repair = {
    "billTo": "677592",
    "shipTo": "677592",
    "diagnosedByTechId": "FIN0825L",
    "diagnosis": data.get("diagnosis"),
    "notes": data.get("diagnosis"),
    "poNumber": "FL" + data.get("order_number"),
    "referenceNumber": po.number,
    "requestReviewByApple": data.get("request_review"),
    "serialNumber": data.get("sn"),
    "symptom": data.get("symptom"),
    "unitReceivedDate": data.get("unitReceivedDate"),
    "unitReceivedTime": data.get("unitReceivedTime")
  }
  
  customer = data.get("customerAddress")
  
  print parts
  
  from gsx.views import submit_repair
  submit_repair(repair, customer, parts)
  
  return HttpResponse("GSX korjaus luotu")
  