# coding=utf-8

from django import forms
from datetime import date, datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render, render_to_response, redirect
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User

from orders.models import *
from orders.forms import *

from devices.models import Device
from customers.models import Customer
from servo.models import Queue, Status, Tag

def close(request, id):
    order = Order.objects.get(pk=id)

    if request.method == "POST":
        order.close(request.user)
        messages.add_message(request, messages.INFO, _(u"Tilaus suljettu"))
        return redirect(order)

    return render(request, "orders/close.html", {'order': order})

@login_required
def create(request, sn=None, product_id=None, note_id=None):
    o = Order.objects.create(created_by=request.user)

    if sn:
        try:
            device = Device.objects.get(sn=sn)
        except Device.DoesNotExist:
            cached = cache.get('warranty-%s' % sn)[0]
            device = Device.objects.create(sn=sn, 
                description=cached.get('productDescription'),
                purchased_on=cached.get('estimatedPurchaseDate'))
            
        o.devices.add(device)
        o.save()

    # creating an order from a product
    if product_id:
        product = Product.objects.get(pk=product_id)
        o.add_product(product)

    if note_id:
        note = Note.objects.get(pk=note_id)
        note.order = o
        note.save()
        # try to match a customer
        if note.mailfrom:
            try:
                customer = Customer.objects.get(contactinfo_value=note.mailfrom)
                order.customer = customer
                order.save()
            except Exception, e:
                print e

    return redirect(o)

@login_required
def search(request):
    queues = Queue.objects.all()
    statuses = Status.objects.all()
    users = User.objects.all()
    locations = Location.objects.all()
    return render(request, 'orders/search.html', {
        'queues': queues,
        'statuses': statuses,
        'users': users,
        'locations': locations})

@login_required
def index(request, *args, **kwargs):
    orders = Order.objects.all()

    if kwargs.get('status'):
        if kwargs['status'] == 'None':
            orders = Order.objects.filter(status__pk=None)
        else:
            orders = Order.objects.filter(status__pk=kwargs['status'])

    if kwargs.get('date'):
        (year, month, day) = kwargs['date'].split('-')
        value = date(int(year), int(month), int(day))
        orders = Order.objects.filter(created_at__startswith=value)

    if kwargs.get('user'):
        orders = Order.objects.filter(user__pk=kwargs['user'])

    if kwargs.get('customer'):
        if kwargs['customer'] == '0':
            orders = Order.objects.filter(customer__pk=None)
        else:
            orders = Order.objects.filter(customer__tree_id=kwargs['customer'])

    if kwargs.get('spec'):
        if kwargs['spec'] == '0':
            orders = Order.objects.filter(devices=None)
        else:
            orders = Order.objects.filter(devices__tags=kwargs['spec'])

    if kwargs.get('device'):
        orders = Order.objects.filter(devices__pk=kwargs['device'])

    if kwargs.get('queue'):
        orders = Order.objects.filter(queue__pk=kwargs['queue'])

    if kwargs.get('tag'):
        orders = Order.objects.filter(tags__pk=kwargs['tag'])

    if kwargs.get('state'):
        orders = Order.objects.filter(state=kwargs['state'])

    if kwargs.get('color'):
        from time import time
        color = kwargs.get('color')
        if color == 'undefined':
            orders = Order.objects.filter(status=None)
        if color == 'green':
            orders = Order.objects.filter(status_limit_green__gte=time())
        if color == 'yellow':
            orders = Order.objects.filter(status_limit_yellow__gte=time())
        if color == 'red':
            orders = Order.objects.filter(status_limit_yellow__lte=time())

    paginator = Paginator(orders, 50)
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    queues = request.user.get_profile().queues.all()
    statuses = Status.objects.all()
    tags = Tag.objects.filter(type='order')
    users = User.objects.all()

    return render(request, "orders/index.html", {
        'tags': tags,
        'users': users,
        'orders': orders,
        'queues': queues,
        'statuses': statuses
        })

def toggle_tag(request, order_id, tag_id):
    order = Order.objects.get(pk=order_id)
    tag = Tag.objects.get(pk=tag_id)

    if tag not in order.tags.all():
        order.tags.add(tag)
        msg = _(u'Tagi %s lisätty' % tag.title)
    else:
        order.tags.remove(tag)
        msg = _(u'Tagi %s poistettu' % tag.title)

    order.save()
    messages.add_message(request, messages.INFO, msg)
    return redirect('/orders/%d/' % order.id)

def edit(request, id):
    o = Order.objects.get(pk=id)
    
    form = SidebarForm(instance=o)
    tags = Tag.objects.filter(type='order')
    fields = Property.objects.filter(type='order')

    # wrap the customer in a list for easier recursetree
    if o.customer:
        customer = o.customer.get_ancestors(include_self=True, ascending=True)
    else:
        customer = []

    request.session['current_order'] = o

    return render(request, 'orders/edit.html', {
        'order': o,
        'tags': tags,
        'form': form,
        'fields': fields,
        'customer': customer
        })

def remove(request, id):
    if request.method == 'POST':
        order = Order.objects.filter(pk=id).delete()
        messages.add_message(request, messages.INFO, 
            _(u'Tilaus %s poistettu' % id))
        return redirect('/orders/')
    else :
        order = Order.objects.get(pk=id)
        return render(request, 'orders/remove.html', {'order': order})

def follow(request, id):
    order = Order.objects.get(pk=id)
    order.followed_by.add(request.user)
    return HttpResponse(_('%d seuraa') % order.followed_by.count())

@csrf_exempt
def update(request, id):
    order = Order.objects.get(pk=id)

    if 'queue' in request.POST:
        order.set_queue(request.POST['queue'], request.user)
    
    if 'status' in request.POST:
        status_id = request.POST.get('status')
        order.set_status(status_id, request.user)
        request.session['current_order'] = order
    
    if 'user' in request.POST:
        order.set_user(request.POST['user'], request.user)
        request.session['current_order'] = order
    
    if 'priority' in request.POST:
        request.session['current_order'].priority = request.POST['priority']
        request.session['current_order'].save()

    return render(request, "orders/events.html", {'order': order})
  
def create_gsx_repair(request, order_id):
    from lib.gsxlib import gsxlib

    order = Order.objects.get(pk=order_id)

    class RepairForm(forms.Form):
        langs = gsxlib.langs("en_XXX")
        symptom_text = order.issues()[0].body
        diagnosis_text = order.issues()[0].replies.all()[0].body
        device = forms.ModelChoiceField(queryset=order.devices.all(), 
            label=_(u'Laite'))

        symptom = forms.CharField(widget=forms.Textarea(attrs={
            'class': 'input-xxlarge', 'rows': 6}), initial=symptom_text)
        diagnosis = forms.CharField(widget=forms.Textarea(attrs={
            'class': 'input-xxlarge', 'rows': 6}), initial=diagnosis_text)

        unitReceivedDate = forms.DateField(initial=order.created_at,
            widget=forms.DateInput(format=langs["df"]),
            input_formats=[langs["df"]])
        unitReceivedTime = forms.TimeField(initial=order.created_at,
            widget=forms.TimeInput(format=langs["tf"]),
            input_formats=[langs["tf"]])

        fileData = forms.FileField(required=False)

    if request.method == "POST":
        customer_form = CustomerForm(request.POST)
        if not customer_form.is_valid():
            messages.add_message(request, messages.ERROR,
                    _(u"Virhe asiakkaan tiedoissa"))
            print customer_form.errors

        repair_form = RepairForm(request.POST)
        
        if not repair_form.is_valid():
            print repair_form.errors

        profile = request.user.get_profile()
        repair = repair_form.cleaned_data
        
        repair['shipTo'] = profile.location.ship_to
        repair['serialNumber'] = repair['device'].sn

        customer_address = customer_form.cleaned_data
        customer_address['state'] = "ZZ"
        customer_address['country'] = "FIN"
        customer_address['regionCode'] = "004"

        if not request.FILES:
            del(repair['fileData'])

        parts = request.POST.getlist("part_numbers")
        comptia_codes = request.POST.getlist("part_codes")
        comptia_modifiers = request.POST.getlist("part_modifiers")
        order_lines = []

        for k, v in enumerate(parts):
            part = dict(partNumber=v, comptiaCode=comptia_codes[k],
                comptiaModifier=comptia_modifiers[k])
            f = PartForm(part)
            if not f.is_valid():
                messages.add_message(request, messages.ERROR,
                    _(u"Tarkista varaosa %s" %v))
                break

            order_lines.append(part)

        repair['orderLines'] = order_lines
        repair['customerAddress'] = customer_address
        print repair

        # data looks good, create Purchase Order...
        po = PurchaseOrder.objects.create(supplier="Apple",
            sales_order=order.id,
            created_by=request.user)

        repair['poNumber'] = str(po.id)

        gsx = GsxAccount.default()
        
        try:
            result = gsx.create_carryin_repair(repair)
            messages.add_message(request, messages.INFO, 
                _(u'Huolto %s luotu' % result[0]['confirmationNumber']))
            return redirect(order)
        except gsxlib.GsxError,e:
            messages.add_message(request, messages.ERROR, e)

    customer = {}
    comptia = gsxlib.symptoms()

    if order.customer:
        customer = order.customer.gsx_address()
    
    profile = request.user.get_profile()

    if not "primaryPhone" in customer:
        customer['primaryPhone'] = profile.location.phone
  
    if not "city" in customer:
        customer['city'] = profile.location.city
  
    if not "addressLine1" in customer:
        customer['addressLine1'] = profile.location.address
  
    if not "zip" in customer:
        customer['zipCode'] = profile.location.zip_code

    if not "emailAddress" in customer:
        customer['emailAddress'] = profile.location.email
        
    parts = []
  
    for p in order.products.all():
        # find the corresponding compnent code from coptia
        try:
            comp = p.component_code
            symptoms = comptia['symptoms'][comp]
            parts.append({"number": p.id, "title": p.title, "code": p.code,
                "symptoms": symptoms})
        except Exception, e:
            # skip products with no GSX data
            continue

    repair_form = RepairForm()
    customer_form = CustomerForm(initial=customer)

    return render_to_response("orders/gsx_repair_form.html", {
        "parts": parts,
        "modifiers": comptia['modifiers'],
        "customer": customer,
        "order": order,
        'customer_form': customer_form,
        'repair_form': repair_form
    })

def put_on_paper(request, order_id, kind='order_template'):
    import pystache
    order = Order.objects.get(pk=order_id)
    conf = Configuration.objects.get(pk=1)
    doc = order.queue.order_template
    tpl = doc.read().decode('utf-8')

    return HttpResponse(pystache.render(tpl, {
        'order': order, 'config': conf
        }))
  
def add_device(request, order_id, device_id=None, sn=None):
    order = Order.objects.get(pk=order_id)

    if device_id:
        device = Device.objects.get(pk=device_id)
    
    if sn:
        cached = cache.get('warranty-%s' % sn)[0]
        device = Device.objects.create(sn=sn, 
            description=cached.get('productDescription'),
            purchased_on=cached.get('estimatedPurchaseDate'))
    
    order.devices.add(device)
    order.save()

    messages.add_message(request, messages.INFO,
        _(u'%s lisätty' % device.description))
    return redirect(order)

def remove_device(request, order_id, device_id):
    order = Order.objects.get(pk=order_id)
    device = Device.objects.get(pk=device_id)
    order.devices.remove(device)
    order.save()
    messages.add_message(request, messages.INFO, _(u'Laite poistettu'))
    
    return redirect(order)

def events(request, order_id):
    order = Order.objects.get(pk=order_id)
    return render(request, "orders/events.html", {"order": order})

def statuses(request, queue_id):
    """List available statuses for this order"""
    from django import forms
    class StatusForm(forms.Form):
        status = forms.ModelChoiceField(
            queryset=QueueStatus.objects.filter(queue=queue_id))

    form = StatusForm()
    return HttpResponse(str(form['status']))

def reserve_products(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(pk=order_id)
        Inventory.objects.filter(slot=order_id, kind='order').delete()
        
        for p in order.serviceorderitem_set.all():
            i = Inventory.objects.create(slot=order_id, product=p.product, 
                kind='order')
        
        Event.objects.create(order=order, kind="products_reserved",
            user=request.user,
            description=_(u"Tilauksen tuotteet varattu"))

        messages.add_message(request, messages.INFO, _(u"Tuotteet varattu"))
        return redirect(order)
    else:
        order = Order.objects.get(pk=order_id)
        return render_to_response("orders/reserve_products.html", {'order': order})

def products(request, order_id, item_id=None, action='list'):
    order = Order.objects.get(pk=order_id)

    if action == "list":
        return render_to_response("orders/products.html", {"order": order})

    if action == 'add':
        product = Product.objects.get(pk=item_id)
        order.add_product(product)
        messages.add_message(request, messages.INFO, 
            _(u'Tuote %d lisätty' % product.id))
        
        return redirect(order)

    if action == 'edit':
        item = ServiceOrderItem.objects.get(pk=item_id)
        form = OrderItemForm(instance=item)

        if request.method == 'POST':
            form = OrderItemForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO,
                    _(u'Tuote tallennettu'))
                
                return redirect(order)

        return render_to_response("orders/edit_product.html", {'order': order,
            'form': form})

    if action == 'remove':
        item = ServiceOrderItem.objects.get(pk=item_id)
        product_id = item.product_id

        if request.method == 'POST':
            item.delete()
            Inventory.objects.filter(slot=item.order_id,
                product_id=product_id).delete()
            messages.add_message(request, messages.INFO, 
                _(u"Tuote %d poistettu tilauksesta" % product_id))
            
            return redirect(order)

        return render_to_response("orders/remove_product.html", {
            'order': order, 'item': item})

    if action == 'report':
        pass

def dispatch(request, order_id=None, numbers=None):
    if request.method == 'POST':
        data = request.POST.copy()
        data.update({'created_by': request.user.pk})
        print data
        form = InvoiceForm(data)
        print form.errors

    order = Order.objects.get(pk=order_id)
    initial = dict(customer=order.customer, customer_name=order.customer.name)
    form = InvoiceForm(initial=initial)
    return render_to_response("orders/dispatch.html", {
        'order': order, 'form': form})

def parts(request, order_id, device_id):
    order = Order.objects.get(pk=order_id)
    device = Device.objects.get(pk=device_id)

    try:
        act = order.queue.gsx_account
        gsx = act.connect()
    except Exception, e:
        gsx = GsxAccount.default()
    
    results = gsx.parts_lookup(device.sn)
    cache.set("gsx-results", results)
    products = Product.objects.filter(tags__pk=device.spec_id)

    return render_to_response("orders/parts.html", {
        'results': results,
        'order': order,
        'device': device,
        'products': products
        })
