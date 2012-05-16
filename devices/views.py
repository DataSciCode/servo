from servo3.models import Device, Order
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.datastructures import DotExpandedDict

from bson.objectid import ObjectId

def index(req):
  """docstring for index"""
  devices = Device.objects
  return render(req, 'devices/index.html', {'devices' : devices})
  
def create(req, order = None, customer = None):
  device = Device()
  
  if order:
    req.session['order'] = Order.objects(id = ObjectId(order)).first()
  
  return render(req, 'devices/form.html', device)
  
def remove(req, id = None):
  if 'id' in req.POST:
    dev = Device.objects(id = ObjectId(req.POST['id']))
    dev.delete()
    return HttpResponse('Laite poistettu')
  else:
    dev = Device.objects(id = ObjectId(id)).first()
    return render(req, 'devices/remove.html', dev)
  
def edit(req, id):
  if id in req.session.get('gsx_data'):
    result = req.session['gsx_data'].get(id)
    print result
    dev = Device(sn = result.get('serialNumber'),\
      description = result.get('productDescription'), gsx_data = result)
  else:
    dev = Device.objects(id = ObjectId(id)).first()
  
  return render(req, 'devices/form.html', dev)
  
def save(req):
  dev = Device()
  
  if 'id' in req.POST:
    dev = Device.objects(id = ObjectId(req.POST['id'])).first()
  
  data = DotExpandedDict(req.POST)
  
  for k, v in data.items():
    dev.__setattr__(k, v)
  
  dev.save()
  
  if req.session['order']:
    req.session['order'].devices.append(dev)
    req.session['order'].save()
  
  return HttpResponse('Laite tallennettu')
  
def search(req):
  return render(req, 'devices/search.html')
  