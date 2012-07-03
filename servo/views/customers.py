import re
from django.shortcuts import render
from django.http import HttpResponse
from servo.models import Customer, Property, Order, ContactInfo

def index(req):
    req.session['order'] = None
    customers = Customer.objects.all()
    return render(req, 'customers/index.html', {'customers': customers})

def search(req):
    return render(req, 'customers/search.html')
  
def create(req, parent = None, order = None):
    fields = Property.objects.filter(type = 'customer')
    customer = Customer()

    if parent:
        parent = Customer.objects.get(pk = parent)
        customer.path = parent.path
    
    return render(req, 'customers/form.html', {'fields' : fields,
        'customer': customer, 'order' : order})

def edit(req, id):
    fields = Property.objects.filter(type = 'customer')

    if id:
        customer = Customer.objects.get(pk = id)

    return render(req, 'customers/form.html', {'fields' : fields,
        'customer': customer})

def save(req):
    """Save either a new or old customer.
    """
    keys = req.POST.getlist('keys')
    values = req.POST.getlist('values')
    props = dict(zip(keys, values))

    if 'id' in req.POST:
        c = Customer.objects.get(pk=req.POST['id'])
        ContactInfo.objects.filter(customer=c).delete()
    else:
        c = Customer(name=req.POST['name'])
        c.save()

    c.name = req.POST.get('name')

    for k, v in props.items():
        if v != '':
            ContactInfo.objects.create(key=k, value=v, customer=c)

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
        c = Customer.objects.get(pk=req.POST['id'])
        c.delete()
        return HttpResponse('Asiakas poistettu')
    else:
        c = Customer.objects.get(pk = id)
        return render(req, 'customers/remove.html', {'customer': c})

def view(req, id):
    c = Customer.objects.get(pk = id)
    return render(req, 'customers/view.html', {'customer': c})

def move(req, id=None):
    """Move a customer under another customer
    @todo: recursively fix paths of child contacts
    """
    if 'id' in req.POST:
        new_parent = Customer.objects.get(pk = req.POST['target'])
        customer = Customer.objects.get(pk = req.POST['id'])
        customer.path = new_parent.path + ',' + str(customer.id)
        customer.save()

        return HttpResponse('Asiakas siirretty')

    if id:
        customer = Customer.objects.get(pk = id)

    return render(req, 'customers/move.html', {'customer': customer})
