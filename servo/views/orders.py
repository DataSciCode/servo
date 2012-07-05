# coding=utf-8
import logging, json, re
from datetime import datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.datastructures import DotExpandedDict
from django.shortcuts import render, render_to_response, redirect

from django.views.decorators.csrf import csrf_exempt
from django import forms
from servo.models import *

class SidebarForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'queue', 'status', 'priority', 'dispatch_method']

def create(request):
    o = Order.objects.create(created_by_id=request.user.id,
        created_at=datetime.now())

    desc = 'Tilaus %d luotu' % o.id
    Event.objects.create(description=desc, order=o,
        kind='create_order', user=request.user)

    return redirect('/orders/%d/' % o.id)

def search(req):
    queues = Queue.objects.all()
    statuses = Status.objects.all()
    users = User.objects.all()
    locations = Location.objects.all()
    return render(req, 'orders/search.html', {'queues': queues,
        'statuses': statuses,
        'users': users,
        'locations': locations})

def index(req, param=None, value=None):
    data = Order.objects.all()

    if param == 'status':
        data = Order.objects.filter(status__pk=value)

    if param == 'user':
        try:
            user = User.objects.get(username=value)
            data = user.order_set.all()
        except Exception, e:
            data = Order.objects.all()

    if param == 'customer':
        customer = Customer.objects.get(pk=value)
        data = customer.order_set.all()

    if param == 'spec':
        spec = Spec.objects.get(pk=value)
        data = Order.objects.filter(devices__spec=spec)

    if param == 'device':
        data = Order.objects.filter(devices__pk=value)

    if param == 'state':
        data = Order.objects.filter(state=value)

    return render(req, 'orders/index.html', {'data': data})

def tags(req, id):
    if 'title' in req.POST:
        order = Order.objects.get(pk=id)
        title = req.POST['title']
    
    if title not in order.tags:
        order.tags.append(title)
        order.save()
    
    if len(Tag.objects(title=title, kind='order')) < 1:
        tag = Tag.objects.create(title=title, kind='order')
    
    return HttpResponse(json.dumps({order.tags}), content_type='application/json')
  
def edit(req, id):
    o = Order.objects.get(pk=id)
    req.session['order'] = o
    
    form = SidebarForm(instance=o)
    users = User.objects.all()
    queues = Queue.objects.all()
    statuses = Status.objects.all()
    priorities = ['Matala', 'Normaali', 'Korkea']
    return render(req, 'orders/edit.html', {
        'order': o,
        'queues': queues,
        'users': users,
        'statuses': statuses,
        'priorities': priorities,
        'form': form
        })

def remove(req, id = None):
    if 'id' in req.POST:
        order = Order.objects.get(pk=req.POST['id'])
        #Inventory.objects(slot = order).delete()
        order.delete()
        return HttpResponse('Tilaus poistettu')
    else :
        order = Order.objects.get(pk=id)
        return render(req, 'orders/remove.html', {'order': order})

def follow(req, id):
    order = Order.objects.get(pk=id)
    order.followed_by.add(req.user)
    return HttpResponse('%d seuraa' % order.followed_by.count())

@csrf_exempt
def update(req, id):
    order = Order.objects.get(pk=id)

    if 'queue' in req.POST:
        queue = Queue.objects.get(pk=req.POST['queue'])
        order.queue = queue
        order.save()
        event = Event.objects.create(description=queue.title,
            order=order,
            kind='set_queue',
            user_id=req.user.id
        )
    
    if 'status' in req.POST:
        from time import time
        status_id = req.POST.get('status')
        status = Status.objects.get(pk=status_id)
        # calculate when this status will timeout
        green = (status.limit_green*status.limit_factor)+time()
        yellow = (status.limit_yellow*status.limit_factor)+time()
        req.session['order'].status_limit_green = green
        req.session['order'].status_limit_yellow = yellow
        req.session['order'].status = status
        req.session['order'].save()

        event = Event.objects.create(description=status.title,
            order=req.session['order'],
            kind='set_status',
            user_id=req.user.id)
    
    if 'user' in req.POST:
        user_id = req.POST['user']

        if user_id == '':
            user = None
            event = u'Käsittelijä poistettu'
            state = 0 # unassigned
        else:
            user = User.objects.get(pk=user_id)
            event = user.username
            state = 1 # open

        req.session['order'].user_id = user.id
        req.session['order'].state = state
        req.session['order'].save()

        Event.objects.create(description=event,
            order=req.session['order'], 
            kind='set_user',
            user_id=req.user.id)
    
    if 'priority' in req.POST:
        req.session['order'].priority = req.POST['priority']
        req.session['order'].save()

    if 'dispatch_method' in req.POST:
        req.session['order'].dispatch_method = req.POST['dispatch_method']
        req.session['order'].save()

    return render(req, 'orders/events.html', {'order': order})
  
def create_gsx_repair(req, order_id):
    order = Order.objects.get(pk=order_id)
    customer = {}
    templates = Message.objects.filter(is_template=True)
    comptia = json.load(open("/Users/filipp/Projects/servo3/gsxlib/symptoms.json"))
  
    if order.customer:
        for p in order.customer.properties():
            v = p.value
            if re.search('@', v):
                customer['emailAddress'] = v
            if re.search('^\d{5}$', v):
                customer['zip'] = v
            if re.search('^\d{6,}$', v):
                customer['primaryPhone'] = v
            if re.search('^\w+\s\d+', v):
                customer['adressLine1'] = v
            if re.search('^[A-Za-z]+$', v):
                customer['city'] = v
  
        (customer['firstName'], customer['lastName']) = order.customer.name.split(" ", 1)
  
    if not "primaryPhone" in customer:
        customer['primaryPhone'] = req.session['user_profile'].location.phone
  
    if not "city" in customer:
        customer['city'] = req.session['user_profile'].location.city
  
    if not "addressLine1" in customer:
        customer['adressLine1'] = req.session['user_profile'].location.address
  
    if not "zip" in customer:
        customer['zip'] = req.session['user_profile'].location.zip
  
    if not "primaryPhone" in customer:
        customer['primaryPhone'] = req.session['user_profile'].location.phone

    if not "emailAddress" in customer:
        customer['emailAddress'] = req.session['user_profile'].location.email
        
    parts = []
  
    for p in order.products.all():
        # find the corresponding compnent code from coptia
        try:
            #comp = p.product.gsx_data['componentCode']
            comp = "B"
            symptoms = comptia['symptoms'][comp]
            parts.append({"number": p.id, "title": p.title,
                "code": p.code, "symptoms": symptoms})
        except Exception, e:
            # skip products with no GSX data
            continue

    return render(req, "orders/gsx_repair_form.html", {
        "templates": templates,
        "parts": parts,
        "modifiers": comptia['modifiers'],
        "customer": customer,
        "order": order
    })

def put_on_paper(req, order_id, template_id, kind='order_template'):
    import pystache
    conf = Configuration.objects.get(pk=1)
    doc = Attachment.objects.get(pk=template_id)
    data = Order.objects.get(pk=order_id)
    tpl = doc.content.read().decode('utf-8')

    return HttpResponse(pystache.render(tpl, {
        'order': data,
        'config': conf,
        'location': req.session.get('user_profile').location
    }))

def submit_gsx_repair(req):
    data = DotExpandedDict(req.POST)
    parts = []
  
    order_number = data.get("order_number");
    order = Order.objects(number = int(order_number)).first()

    # create Purchase Order
    po = PurchaseOrder(supplier = "Apple", reference = order_number)
    po.save()
  
    for k, v in data.get("items").items():
        # add to "ordered" inventory
        p = Product.objects(code = v['partNumber']).first()
        Inventory(kind = "po", product = p, slot = po).save()
        Inventory(kind = "order", product = p, slot = order).save()
        parts.append(v)
    
    po.products = parts
    po.carrier = "UPS"
    po.save()
  
    repair = {
        "billTo": "677592",
        "shipTo": "677592",
        "diagnosis": data.get("diagnosis"),
        "notes": data.get("diagnosis"),
        "poNumber": "FL" + order_number,
        "referenceNumber": po.number,
        "requestReviewByApple": data.get("request_review"),
        "serialNumber": data.get("sn"),
        "symptom": data.get("symptom"),
        "unitReceivedDate": data.get("unitReceivedDate"),
        "unitReceivedTime": data.get("unitReceivedTime")
    }
  
    customer = data.get("customerAddress")

    try:
        gsx_repair = submit_repair(repair, customer, parts)
    except Exception, e:
        return HttpResponse(e)

    po.confirmation = gsx_repair['confirmationNumber']
    po.save()
    
    order = Order.objects(number=int(order_number)).first()
    order.gsx_repairs.append(gsx_repair)
    
    return HttpResponse("GSX korjaus luotu")
  
def messages(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, "orders/messages.html", {"order": order})
  
def issues(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, 'orders/issues.html', {'order': order})
  
def devices(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, "orders/devices.html", {"order": order})
  
def events(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, "orders/events.html", {"order": order})
  
def customer(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, "orders/customer.html", {"order": order})

def statuses(req):
    statuses = req.session.get('order').queue.statuses.all()
    return render(req, "orders/statuses.html", {"statuses": statuses})

def products(req, order_id):
    order = Order.objects.get(pk=order_id)
    return render(req, "orders/products.html", {"order": order})
