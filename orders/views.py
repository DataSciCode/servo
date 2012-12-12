# coding=utf-8

from django import forms
from datetime import date, datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render, redirect
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
from notes.models import Note
from gsx.models import Lookup

def close(request, id):
    order = Order.objects.get(pk=id)

    if request.method == "POST":
        order.close(request.user)
        messages.add_message(request, messages.INFO, _(u"Tilaus suljettu"))
        return redirect(order)

    return render(request, 'orders/close.html', {'order': order})

@login_required
def create(request, sn=None, product_id=None, note_id=None):
    order = Order.objects.create(created_by=request.user)

    if sn:
        try:
            device = Device.objects.get(sn=sn)
        except Device.DoesNotExist:
            cached = cache.get('warranty-%s' % sn)[0]
            device = Device.objects.create(sn=sn, 
                description=cached.get('productDescription'),
                purchased_on=cached.get('estimatedPurchaseDate'))
            
        order.devices.add(device)
        order.save()

    # creating an order from a product
    if product_id:
        product = Product.objects.get(pk=product_id)
        order.add_product(product)

    if note_id:
        note = Note.objects.get(pk=note_id)
        note.order = order
        note.save()
        # try to match a customer
        if note.sender:
            try:
                customer = Customer.objects.get(email=note.sender)
                order.customer = customer
                order.save()
            except Customer.DoesNotExist:
                pass

    return redirect(order)

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

def index(request, *args, **kwargs):
    orders = Order.objects.all()
    status_title = _('Status')

    if kwargs.get('date'):
        (year, month, day) = kwargs['date'].split('-')
        value = date(int(year), int(month), int(day))
        orders = Order.objects.filter(created_at__startswith=value)

    if kwargs.get('user'):
        orders = Order.objects.filter(user__pk=kwargs['user'])
        if request.is_ajax():
            return HttpResponse(orders.filter(state=1).count())

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

    if request.GET.get('status'):
        status = int(request.GET.get('status'))
        if status == 'None':
            orders = Order.objects.filter(status__pk=None)
        else:
            status = Status.objects.get(pk=status)
            status_title = status.title
            print status_title
            orders = Order.objects.filter(status=status)

    if request.is_ajax():
        return HttpResponse(orders.filter(state=0).count())

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
        'statuses': statuses,
        'status_title': status_title
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


def submit_gsx_repair(request):
    pass    

def create_gsx_repair(request, order_id):
    from lib.gsxlib import gsxlib

    parts = list()
    order = Order.objects.get(pk=order_id)
    comptia = gsxlib.CompTia().symptoms()

    for p in order.serviceorderitem_set.all():
        # find the corresponding compnent code from coptia
        try:
            comp = p.product.component_code
            symptoms = comptia[comp]
            parts.append({
                'number': p.id,
                'title': p.title,
                'code': p.product.code,
                'symptoms': symptoms
            })
        except Exception, e:
            print e
            # skip products with no GSX data
            continue

    profile = request.user.get_profile()
    customer = {}

    if order.customer:
        customer = order.customer.gsx_address()
    else:
        messages.add_message(request, messages.ERROR,
            _('Tilauksesta puuttuu asiakastiedot'))
        return redirect(order)

    if request.method == 'POST':
        customer_form = GsxCustomerForm(request.POST, profile=profile, 
            customer=customer)

        if not customer_form.is_valid():
            print customer_form.errors
            messages.add_message(request, messages.ERROR,
                    _(u'Virhe asiakkaan tiedoissa'))

        repair_form = GsxRepairForm(request.POST, order=order)
        
        if not repair_form.is_valid():
            print repair_form.errors

        repair = repair_form.cleaned_data

        repair['serialNumber'] = repair['device'].sn
        repair['diagnosedByTechId'] = profile.tech_id

        customer_address = customer_form.cleaned_data
        customer_address['country'] = customer_address['country'].iso3

        # @todo: where should we put these?
        customer_address['state'] = 'ZZ'
        customer_address['regionCode'] = '004'
        repair['customerAddress'] = customer_address

        if not request.FILES:
            del(repair['fileData'])
        else:
            pass

        abused = request.POST.getlist('abused')
        parts = request.POST.getlist('part_numbers')
        comptia_codes = request.POST.getlist('part_codes')
        comptia_modifiers = request.POST.getlist('part_modifiers')
        order_lines = []

        for k, v in enumerate(parts):
            part = {'partNumber': v, 'comptiaCode': comptia_codes[k],
                'comptiaModifier': comptia_modifiers[k],
                'abused': abused[k]}

            f = GsxPartForm(part)

            if not f.is_valid():
                print f.errors
                messages.add_message(request, messages.ERROR,
                    _(u'Tarkista varaosa %s' % v))
                break
            else:
                order_lines.append(f.cleaned_data)
 
        repair['orderLines'] = order_lines

        # data looks good, create Purchase Order...
        po = PurchaseOrder.objects.create(supplier='Apple',
            sales_order=order,
            created_by=request.user)

        # ... and add the parts to the PO
        # @todo: link part to ServiceOrderItem
        ids = request.POST.getlist('ids')

        for p in ids:
            soi = ServiceOrderItem.objects.get(pk=p)
            PurchaseOrderItem.objects.create(
                code=soi.code, 
                order_item=soi,
                price=soi.price,
                purchase_order=po,
                product=soi.product,
                date_ordered=datetime.now())

        repair['poNumber'] = str(po.id)
        del(repair['device'])

        try:
            act = order.queue.gsx_account
            gsx = act.connect()
            repair['shipTo'] = act.ship_to
        except Exception, e:
            print e
            print "Using default GSX account..."
            repair['shipTo'] = profile.location.ship_to
            gsx = GsxAccount.default()
        
        try:
            result = gsx.create_carryin_repair(repair)
            confirmation = result[0]['confirmationNumber']
            po.confirmation = confirmation
            po.save()
            description =  _(u'GSX huolto %s luotu' % confirmation)
            order.notify('gsx_repair_created', description, request.user)
            messages.add_message(request, messages.INFO, description)
            return redirect(order)
        except gsxlib.GsxError, e:
            messages.add_message(request, messages.ERROR, e)
    
    repair_form = GsxRepairForm(order=order)
    customer_form = GsxCustomerForm(profile=profile, 
        customer=customer,
        initial={'country': profile.location.country})

    return render(request, 'orders/gsx_repair_form.html', {
        'parts': parts,
        'modifiers': gsxlib.CompTia().modifiers,
        'order': order,
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
            p.product.amount_reserved = p.product.amount_reserved + p.amount
            p.product.save()
        
        description = _(u'Tilauksen %s tuotteet varattu' % order.code)

        Event.objects.create(ref='order', ref_id=order.id,
            action='products_reserved',
            triggered_by=request.user,
            description=description)

        messages.add_message(request, messages.INFO, _(u'Tuotteet varattu'))
        return redirect(order)
    else:
        order = Order.objects.get(pk=order_id)
        return render(request, 'orders/reserve_products.html', {'order': order})

def products(request, order_id, item_id=None, action='list'):
    order = Order.objects.get(pk=order_id)

    if action == 'list':
        return render(request, 'orders/products.html', {"order": order})

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

        return render(request, "orders/edit_product.html", {'order': order,
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

        return render(request, "orders/remove_product.html", {
            'order': order, 'item': item})

    if action == 'report':
        pass

def dispatch(request, order_id=None, numbers=None):
    order = Order.objects.get(pk=order_id)
    products = order.serviceorderitem_set.filter(dispatched=False)

    if request.method == 'POST':
        total_margin = order.total_margin()
        invoice = Invoice(created_by=request.user, order=order, 
            customer=order.customer, total_margin=total_margin)
        
        form = InvoiceForm(request.POST, instance=invoice)
        
        if not form.is_valid():
            return render(request, "orders/dispatch.html", {
                'form': form, 'order': order, 'products': products
                })
        
        invoice = form.save()
        products = request.POST.getlist('items')

        for p in products:
            soi = ServiceOrderItem.objects.get(pk=p)
            InvoiceItem.objects.create(invoice=invoice, price=soi.price, 
                product=soi.product)
            
            soi.product.sell(soi.amount)

        messages.add_message(request, messages.INFO, _(u'Tilaus toimitettu'))
        return redirect(order)

    initial = dict(order=order,
        total_notax=order.net_total(),
        total_sum=order.gross_total(),
        total_tax=order.total_tax())

    if order.customer:
        initial['customer'] = order.customer, 
        initial['customer_name'] = order.customer.name,
        initial['customer_phone'] = order.customer.phone,
        initial['customer_email'] = order.customer.email,
        initial['customer_address'] = order.customer.street_address,
    else:
        initial['customer_name'] = _(u'Käteisasiakas')

    form = InvoiceForm(initial=initial)

    return render(request, 'orders/dispatch.html', {
        'order': order, 'form': form, 'products': products})

def parts(request, order_id, device_id):
    # List available parts for this device/order
    # taking into account the order's queues GSX account...
    order = Order.objects.get(pk=order_id)
    device = Device.objects.get(pk=device_id)

    try:
        act = order.queue.gsx_account
        gsx = act.connect()
    except Exception, e:
        print "Using default GSX account..."
        gsx = GsxAccount.default()
    
    results = Lookup(gsx).lookup(device.sn)
    products = Product.objects.filter(tags__pk=device.spec_id)

    return render(request, "orders/parts.html", {
        'results': results,
        'order': order,
        'device': device,
        'products': products
        })
