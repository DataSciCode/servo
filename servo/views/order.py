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

from django.views.generic import TemplateView

from servo.models.order import *
from servo.forms.order import *

from servo.models.device import Device
from servo.models.customer import Customer
from servo.models.common import Queue, Status, Tag
from servo.models.note import Note
from servo.models.gsx import Lookup, GsxAccount

class ModalView(TemplateView):
    template = 'modal.html'

def close(request, id):
    order = Order.objects.get(pk=id)

    if request.method == "POST":
        order.close(request.user)
        messages.add_message(request, messages.INFO, _(u"Tilaus suljettu"))
        return redirect(order)

    return render(request, 'orders/close.html', {'order': order})

@login_required
def create(request, sn=None, product_id=None, note_id=None):

    profile = request.user.get_profile()
    order = Order.objects.create(created_by=request.user)

    if sn:
        try:
            device = Device.objects.get(sn=sn)
        except Device.DoesNotExist:
            GsxAccount.default()
            device = Device.from_gsx(sn)
            
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
    """
    Lists service orders matching specified criteria
    """

    location = request.user.get_profile().location
    orders = Order.objects.filter(location=location)

    if kwargs.get('date'):
        (year, month, day) = kwargs['date'].split('-')
        value = date(int(year), int(month), int(day))
        orders = Order.objects.filter(created_at__startswith=value)

    if kwargs.get('user'):
        user = User.objects.get(pk=kwargs['user'])
        user_title = user.get_full_name()
        orders = orders.filter(user=user)

        if request.is_ajax():
            return HttpResponse(orders.filter(state=1).count())

    if kwargs.get('customer'):
        if kwargs['customer'] == '0':
            orders = orders.filter(customer__pk=None)
        else:
            orders = orders.filter(customer__tree_id=kwargs['customer'])

    if kwargs.get('spec'):
        if kwargs['spec'] == '0':
            orders = orders.filter(devices=None)
        else:
            orders = orders.filter(devices__tags=kwargs['spec'])

    if kwargs.get('device'):
        orders = order.filter(devices__pk=kwargs['device'])

    if kwargs.get('queue'):
        queue = Queue.objects.get(pk=kwargs['queue'])
        orders = orders.filter(queue=queue)
        queue_title = queue.title
        #orders = Order.objects.filter(queue__pk=kwargs['queue'])

    if request.GET.get('tag'):
        tag = Tag.objects.get(pk=request.GET.get('tag'))
        tag_title = tag.title
        orders = orders.filter(tags=tag)

        if request.is_ajax():
            return HttpResponse(orders.count())

    if kwargs.get('state'):
        status_title = _(u'Jonossa')
        orders = orders.filter(state=kwargs['state'])

    if kwargs.get('color'):
        from time import time
        color = kwargs.get('color')
        if color == 'undefined':
            orders = orders.filter(status=None)
        if color == 'green':
            orders = orders.filter(status_limit_green__gte=time())
        if color == 'yellow':
            orders = orders.filter(status_limit_yellow__gte=time())
        if color == 'red':
            orders = orders.filter(status_limit_yellow__lte=time())

    if request.GET.get('status'):
        if request.GET.get('status') == 'None':
            orders = orders.filter(status__pk=None)
        else:
            status = int(request.GET.get('status'))
            orders = orders.filter(status__status_id=status)

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

    return render(request, 'orders/index.html', {
        'tags': Tag.objects.filter(type='order'),
        'users': User.objects.filter(userprofile__location=location),
        'orders': orders,
        'queues': queues,
        'statuses': Status.objects.all(),
        })

def toggle_tag(request, order_id, tag_id):
    tag = Tag.objects.get(pk=tag_id)
    order = Order.objects.get(pk=order_id)

    if tag not in order.tags.all():
        order.tags.add(tag)
    else:
        order.tags.remove(tag)

    order.save()
    
    return HttpResponse(tag.title)

def edit(request, order_id):
    order = Order.objects.get(pk=order_id)
    
    class SidebarForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(SidebarForm, self).__init__(*args, **kwargs)
            if kwargs['instance'].queue:
                self.fields['status'] = forms.ModelChoiceField(queryset=order.queue.queuestatus_set.all())

        class Meta:
            model = Order
            fields = ('user', 'queue', 'status', 'priority',)
            widgets = {
                'status': forms.Select(attrs={'disabled': 'disabled'})
            }

    form = SidebarForm(instance=order)

    tags = Tag.objects.filter(type='order')
    fields = Property.objects.filter(type='order')

    # wrap the customer in a list for easier recursetree
    if order.customer:
        customer = order.customer.get_ancestors(include_self=True)
    else:
        customer = []

    request.session['current_order'] = order
    users_menu = dict(title=_(u'Käsittelijä'), users=[])

    for user in User.objects.all():
        users_menu['users'].append(user)

    queue_menu = dict(title=_(u'Jono'), queues=[])
    for q in Queue.objects.all():
        queue_menu['queues'].append(q)

    return render(request, 'orders/edit.html', {
        'order': order,
        'tags': tags,
        'form': form,
        'fields': fields,
        'customer': customer,
        'users_menu': users_menu,
        'queue_menu': queue_menu
        })

def remove(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(pk=order_id)
        order.delete()
        messages.add_message(request, messages.INFO, 
            _(u'Tilaus %s poistettu' % order.code))
        return redirect('/orders/')
    else:
        order = Order.objects.get(pk=order_id)
        return render(request, 'orders/remove.html', {'order': order})

def follow(request, order_id):
    order = Order.objects.get(pk=order_id)
    order.followed_by.add(request.user)
    return HttpResponse(_('%d seuraa') % order.followed_by.count())

@csrf_exempt
def update(request, order_id):
    order = Order.objects.get(pk=order_id)

    if 'queue' in request.POST:
        order.set_queue(request.POST['queue'], request.user)
    
    if 'status' in request.POST:
        status_id = request.POST.get('status')
        order.set_status(status_id, request.user)
    
    if 'user' in request.POST:
        order.set_user(request.POST['user'], request.user)
    
    if 'priority' in request.POST:
        order.priority = request.POST['priority']
        order.save()

    request.session['current_order'] = order
    return render(request, 'orders/events.html', {'order': order})

def submit_gsx_repair(request):
    pass    

def create_gsx_repair(request, order_id):
    from servo.lib.gsx import gsx

    parts = list()
    order = Order.objects.get(pk=order_id)
    comptia = gsx.CompTia().symptoms()

    # find the corresponding compnent code from coptia
    for p in order.serviceorderitem_set.all():
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
    
    if len(parts) < 1:
        messages.add_message(request, messages.ERROR, 
            _(u'Tilauksessa ei ole yhtään tilattavaa osaa'))
        return redirect(order)

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
            part = {
                'partNumber': v,
                'comptiaCode': comptia_codes[k],
                'comptiaModifier': comptia_modifiers[k],
                'abused': abused[k]
                }

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
            act.connect()
            repair['shipTo'] = act.ship_to
        except Exception, e:
            print e
            repair['shipTo'] = profile.location.ship_to
            GsxAccount.default()
        
        try:
            print repair
            rep = gsx.Repair(**repair)
            result = rep.create_carryin()
            confirmation = result.confirmationNumber
            po.confirmation = confirmation
            po.date_submitted = datetime.now()
            po.save()
            description =  _(u'GSX huolto %s luotu' % confirmation)
            order.notify('gsx_repair_created', description, request.user)
            messages.add_message(request, messages.INFO, description)
            return redirect(order)
        except Exception, e:
            messages.add_message(request, messages.ERROR, e)
    
    repair_form = GsxRepairForm(order=order)
    customer_form = GsxCustomerForm(profile=profile, 
        customer=customer,
        initial={'country': profile.location.country})

    return render(request, 'orders/gsx_repair_form.html', {
        'parts': parts,
        'modifiers': gsx.CompTia().modifiers,
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
        act = GsxAccount.default()
        device = Device.from_gsx(sn)
    
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
        return render(request, 'orders/products.html', {'order': order})

    if action == 'report':
        product = ServiceOrderItem.objects.get(pk=item_id)
        product.should_report = not product.should_report
        product.save()
        return HttpResponse('OK')

    if action == 'add':
        product = Product.objects.get(pk=item_id)
        oi = order.add_product(product)
        messages.add_message(request, messages.INFO, 
            _(u'Tuote %d lisätty' % product.id))
        
        return redirect('%s/products/%d/edit/' %(order.get_absolute_url(), oi.id))

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

        return render(request, 'orders/edit_product.html', {
            'order': order,
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

        return render(request, 'orders/remove_product.html', {
            'order': order, 'item': item})

    if action == 'report':
        pass

def dispatch(request, order_id=None, numbers=None):
    order = Order.objects.get(pk=order_id)
    products = order.serviceorderitem_set.filter(dispatched=False)

    if request.method == 'POST':
        total_margin = order.total_margin()
        invoice = Invoice(
            created_by=request.user,
            order=order, 
            customer=order.customer,
            total_margin=total_margin)
        
        form = InvoiceForm(request.POST, instance=invoice)
        
        if not form.is_valid():
            return render(request, 'orders/dispatch.html', {
                'form': form, 'order': order, 'products': products
                })
        
        invoice = form.save()
        products = request.POST.getlist('items')

        for p in products:
            soi = ServiceOrderItem.objects.get(pk=p)
            InvoiceItem.objects.create(invoice=invoice, price=soi.price, 
                product=soi.product)
            
            soi.product.sell(soi.amount)
            soi.dispatched = True
            soi.save()

        messages.add_message(request, messages.INFO, _(u'Tilaus toimitettu'))
        return redirect(order)

    initial = dict(order=order,
        total_notax=order.net_total(),
        total_sum=order.gross_total(),
        total_tax=order.total_tax())

    if order.customer:
        customer = order.customer
        initial['customer_name'] = customer.name,
        initial['customer_phone'] = customer.phone,
        initial['customer_email'] = customer.email,
        initial['customer_address'] = customer.street_address,
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
