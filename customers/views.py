from django.shortcuts import render
from django.http import HttpResponse

from servo3.models import Customer, Field

def index(req):
  return render(req, 'customers/index.html', Customer.objects)

def edit(req, id=None):
  fields = Field.objects(type='customer')
  customer = Customer()
  return render(req, 'customers/form.html', {'fields' : fields, 'customer': customer})

def save(req):
  print req.POST
  for t in req.POST['properties']['title']:
    print t
  
  return HttpResponse('')
