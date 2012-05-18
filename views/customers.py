import re
from django.shortcuts import render
from django.http import HttpResponse

from bson.objectid import ObjectId
from servo3.models import Customer, Field, Order

def index(req):
  customers = Customer.objects
  return render(req, 'customers/index.html', {'customers' : customers})

def search(req):
  return render(req, 'customers/search.html')
  
def create(req, parent=None, order=None):
  fields = Field.objects(type='customer')
  customer = Customer()
  
  if parent:
    parent = Customer.objects(id=ObjectId(parent))[0]
    customer.path = parent.path
  
  return render(req, 'customers/form.html', {'fields' : fields, 'customer': customer, 'order' : order})
  
def edit(req, id):
  fields = Field.objects(type='customer')
  if id:
    customer = Customer.objects(id=ObjectId(id))[0]
  
  return render(req, 'customers/form.html', {'fields' : fields, 'customer': customer})

def save(req):
  """
  Save either a new or old customer.
  @todo: handling of properties with empty values
  """
  keys = req.POST.getlist('keys')
  values = req.POST.getlist('values')
  props = dict(zip(keys, values))
  c = Customer()
  
  if 'id' in req.POST:
    c = Customer.objects(id=ObjectId(req.POST['id']))[0]
  
  c.name = req.POST['name']
  c.properties = props
  c.save()
  
  c.path = req.POST.get('path', str(c.id))
  
  if 'path' in req.POST:
    if not re.search(str(c.id), c.path):
      c.path += ',' + str(c.id) # adding a contact for an existing customer
  
  if req.session.get('order'):
    req.session['order'].customer = c
    req.session['order'].save()
  
  c.save()
  
  return HttpResponse('Asiakas tallennettu')

def remove(req, id=None):
  if 'id' in req.POST:
    c = Customer.objects(id=ObjectId(req.POST['id']))
    c.delete()
    return HttpResponse('Asiakas poistettu')
  else:
    c = Customer.objects(id=ObjectId(id))[0]
    return render(req, 'customers/remove.html', c)

def view(req, id):
  c = Customer.objects(id=ObjectId(id))[0]
  return render(req, 'customers/view.html', {'customer': c })

def move(req, id=None):
  """
  Move a customer under another customer
  @todo: recursively fix paths of child contacts
  """
  if 'id' in req.POST:
    new_parent = Customer.objects(number = int(req.POST['number']))[0]
    customer = Customer.objects(id = ObjectId(req.POST['id']))[0]
    customer.path = new_parent.path + ',' + str(customer.id)
    customer.save()
    
    return HttpResponse('Asiakas siirretty')
    
  if id:
    customer = Customer.objects(id=ObjectId(id))[0]
  
  return render(req, 'customers/move.html', customer)
