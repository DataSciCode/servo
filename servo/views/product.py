#coding=utf-8

from decimal import *
from django.contrib import messages
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect, render_to_response
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.models.gsx import Lookup, GsxAccount
from servo.models.common import *
from servo.models.order import *
from servo.models.product import *

from servo.forms.product import ProductForm, PurchaseOrderForm, PurchaseOrderItemForm

def index(request, tag_id=None, spec_id=None):
    title = _(u'Ryhmä')
    all_products = Product.objects.all()

    if request.is_ajax():
        return HttpResponse(all_products.count())

    if spec_id:
        all_products = Product.objects.filter(specs=spec_id)

    if tag_id:
        all_products = Product.objects.filter(tags__pk=tag_id)

    tags = Tag.objects.filter(type='product')
    specs = Tag.objects.filter(type='device')

    page = request.GET.get('page')
    paginator = Paginator(all_products, 50)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/index.html', {
        'products': products,
        'tags': tags,
        'title': title,
        'specs': specs,
        })

def edit(request, product_id=0, code=None):
    
    if request.method == 'POST':
        return save(request, product_id)

    result = {}
    form = ProductForm()

    if int(product_id) > 0:
        product = Product.objects.get(pk=product_id)
        form = ProductForm(instance=product)
        product_id = product.id
    
    if code:
        # We shoose the GSX account here since orders in different queues
        # might use a different accounts...
        act = GsxAccount.default()
        product = Product.from_gsx(code, act)
        form = ProductForm(instance=product)
    
    return render(request, 'products/form.html', {
        'form': form
        })

def remove(request, id):
    if 'id' in request.POST:
        product = Product.objects.get(pk=request.POST['id']);
        Inventory.objects.filter(product=product).delete()
        product.delete()
        messages.add_message(request, messages.INFO, _(u'Tuote poistettu'))
        return redirect('/products/')
    else:
        product = Product.objects.get(pk=id)

    return render(request, 'products/remove.html', {'product': product})

def save(request, product_id):
    """
    Save a product
    """
    form = ProductForm(request.POST)

    if int(product_id) > 0:
        product = Product.objects.get(pk=product_id)
        form = ProductForm(request.POST, instance=product)
        
    if not form.is_valid():
        messages.add_message(request, messages.ERROR, _(u'Tarkista tuotteen tiedot'))
        return render(request, 'products/form.html', {
            'form': form, 'product_id': product_id
            })
        
    product = form.save()
    data = form.cleaned_data

    try:
        if product.code in request.session.get('gsx_data'):
            gsx_data = request.session['gsx_data'].get(product.code)
            for k, v in gsx_data.items():
                GsxData.objects.create(key=k, value=v,
                    references="product", reference_id=product.id)
    except Exception, e:
        print form.errors

    #product.tags = request.POST.getlist('tags')
    
    for a in request.POST.getlist('attachments'):
        doc = Attachment.objects.get(pk=a)
        product.attachments.add(doc)
    
    messages.add_message(request, messages.INFO, 
        _(u'Tuote %s tallennettu' % product.code))
    
    return redirect('/products/')
    
def search(request):
    return render(request, 'products/search.html')

def view(request, product_id=None, code=None):

    product = Product()
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        gsx = GsxAccount.default()
        product = gsx.parts_lookup({'partNumber': code})[0]
        product = ServicePart(product)
    
    return render(request, 'products/view.html', {'product': product})

def invoices(request):
    invoices = Invoice.objects.all()

    if request.is_ajax():
        return HttpResponse(invoices.count())

    page = request.GET.get('page')
    paginator = Paginator(invoices, 50)

    try:
        invoices = paginator.page(page)
    except PageNotAnInteger:
        invoices = paginator.page(1)
    except EmptyPage:
        invoices = paginator.page(paginator.num_pages)

    return render(request, "products/invoices.html", {'invoices': invoices})
  
def create_po(request, product_id=None, order_id=None):
    if order_id:
        po = PurchaseOrder.objects.create(created_by=request.user, 
            sales_order_id=order_id)

        for i in ServiceOrderItem.objects.filter(order_id=order_id):
            po.add_product(i)
    else:
        po = PurchaseOrder.objects.create(created_by=request.user)

    if product_id:
        product = Product.objects.get(pk=product_id)
        PurchaseOrderItem.objects.create(code=product.code,
            amount=1,
            purchase_order=po,
            product_id=product.id, 
            price=product.price_purchase)

    messages.add_message(request, messages.INFO,
        _(u'Ostotilaus %d luotu' % po.pk))

    return redirect(po)

def edit_po(request, id, item_id=None, action='add'):
    po = PurchaseOrder.objects.get(pk=id)
    form = PurchaseOrderForm(instance=po)

    if request.method == 'POST':
        data = request.POST.copy()
        data['created_by'] = request.user.id
        form = PurchaseOrderForm(data, instance=po)

        if not form.is_valid():
            return render(request, 'products/purchase_order.html', {
                'form': form, 'order': po
                })
            
        form.save()
        messages.add_message(request, messages.INFO,
            _(u'Ostotilaus tallennettu'))

        items = request.POST.getlist('items')
        prices = request.POST.getlist('prices')
        amounts = request.POST.getlist('amounts')
        
        for k, v in enumerate(items):
            item = PurchaseOrderItem.objects.get(pk=v)
            item.amount = int(amounts[k])
            item.price = prices[k]
            d = dict(amount=amounts[k], price=prices[k], 
                product=item.product.id,
                title=item.product.title,
                code=item.product.code)
            
            f = PurchaseOrderItemForm(d, instance=item)

            if not f.is_valid():
                print f.errors
                messages.add_message(request, messages.ERROR,
                    _('Tarkista tuote %s' % item.product.code))
                break

            f.save()

        return redirect('/products/po/')

    if item_id and action == 'add':
        product = Product.objects.get(pk=item_id)
        poi = PurchaseOrderItem.objects.create(code=product.code,
            purchase_order=po,
            product_id=product.id, 
            price=product.price_purchase)

        messages.add_message(request, messages.INFO, 
            _(u'Tuote #%d lisätty' % product.id))

        return redirect(po)

    if item_id and action == 'remove':
        poi = PurchaseOrderItem.objects.get(pk=item_id)
        pid = poi.product_id
        Inventory.objects.filter(slot=poi.purchase_order_id, 
            product_id=pid).delete()
        poi.delete()

        messages.add_message(request, messages.INFO, 
            _(u'Tuote #%d poistettu' % pid))

        return redirect(po)
    
    request.session['current_po'] = po

    return render(request, 'products/purchase_order.html', {'order': po,
        'form': form})

def submit_po(request, id):
    po = PurchaseOrder.objects.get(pk=id)
    po.submit()
    messages.add_message(request, messages.INFO, _(u'Ostotilaus lähetetty'))
    return redirect('/products/po/')
  
def index_po(request):
    all_orders = PurchaseOrder.objects.all()

    if request.is_ajax():
        return HttpResponse(all_orders.filter(has_arrived=False).count())

    page = request.GET.get('page')
    paginator = Paginator(all_orders, 50)

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'products/purchase_orders.html', {'orders': orders})

def order_stock(request, po_id):
    from lib.gsxlib import gsxlib
    po = PurchaseOrder.objects.get(pk=po_id)
    gsx = GsxAccount.default()
    items = []
    for i in po.purchaseorderitem_set.all():
        items.append({'partNumber': i.code, 'quantity': str(i.amount)})

    try:
        profile = request.user.get_profile()
        ship_to = profile.location.ship_to
        so = gsx.create_stocking_order(purchaseOrderNumber=str(po.id),
        shipToCode=ship_to,
        orderLines=items)
    except gsxlib.GsxError, e:
        messages.add_message(request, messages.ERROR, e)

    return redirect('/products/po/')

def remove_po(request, po_id):
    PurchaseOrder.objects.filter(pk=po_id).delete()
    messages.add_message(request, messages.INFO, 
        _(u'Ostotilaus %s poistettu' % po_id))

    return redirect('/products/po/')

def index_incoming(request, shipment=None, date=None, status=''):
    """
    Lists purchase order items that have not arrived yet
    """
    inventory = PurchaseOrderItem.objects.filter(date_received=None)

    if request.is_ajax():
        return HttpResponse(inventory.count())

    if request.POST.getlist('id'):
        count = len(request.POST.getlist('id'))
        
        for i in request.POST.getlist('id'):
            item = PurchaseOrderItem.objects.get(pk=i)
            item.date_received = datetime.now()
            item.received_by = request.user
            item.save()
        
        messages.add_message(request, messages.INFO, 
            _(u'%d tuotetta saavutettu' % count))

        return redirect('/products/incoming/')

    if request.GET.get('i'):
        item = PurchaseOrderItem.objects.get(pk=request.GET['i'])

        if request.method == 'POST':
            item.date_received = datetime.now()
            item.received_by = request.user
            form = PurchaseOrderItemForm(request.POST, instance=item)
            if form.is_valid():
                item = form.save()
                if item.order_item: # copy SN from POI to SOI
                    item.order_item.sn = item.sn
                    item.order_item.save()
                messages.add_message(request, messages.INFO, 
                    _(u'Tuote %s saavutettu' % item.code))
        else:
            form = PurchaseOrderItemForm(instance=item)

        return render(request, 'products/receive_item.html', {
            'form': form,
            'item': item
            })

    return render(request, 'products/index_incoming.html',
        {'inventory': inventory})
  
def index_outgoing(request, shipment=None, date=None):
    if request.is_ajax():
        return HttpResponse('5')

    inventory = ServiceOrderItem.objects.filter(should_return=True)
    return render(request, 'products/index_outgoing.html', {'inventory': inventory})
