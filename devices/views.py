from servo3.models import Device, Order
from django.shortcuts import render
from django.http import HttpResponse

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
    dev = Device(sn = result.get('serialNumber'),\
      description = result.get('productDescription'), gsx_data = result)
  else:
    dev = Device.objects(id = ObjectId(id)).first()
  
  return render(req, 'devices/form.html', dev)
  
def save(req):
  dev = Device()
  
  if 'id' in req.POST:
    dev = Device.objects(id = ObjectId(req.POST['id'])).first()
  
  dev.sn = req.POST.get('sn')
  dev.notes = req.POST.get('notes')
  dev.username = req.POST.get('username')
  dev.password = req.POST.get('password')
  dev.description = req.POST.get('description')
  dev.purchased_on = req.POST.get('purchased_on')
  
  dev.save()
  
  if req.session['order']:
    req.session['order'].devices.append(dev)
    req.session['order'].save()
  
  return HttpResponse('Laite tallennettu')
  
def search(req):
  return render(req, 'devices/search.html')
  