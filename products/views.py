#coding=utf-8

from decimal import *
from django import forms
from django.contrib import messages
from django.http import HttpResponse
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from servo.models import *
from products.models import *
from orders.models import PurchaseOrder, PurchaseOrderItem, Invoice

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('files')

	description = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}))
    amount_stocked = forms.CharField(max_length=3, required=False)

def index(request, group_id=None, tag_id=None, spec_id=None):
    title = _('Kaikki')
    all_products = Product.objects.all()

    if group_id:
        group = ProductGroup.objects.get(pk=group_id)
        title = group.name
        all_products = Product.objects.filter(group_id=group_id)

    if spec_id:
        all_products = Product.objects.filter(specs=spec_id)

    if tag_id:
        all_products = Product.objects.filter(tags__pk=tag_id)

    tags = Tag.objects.filter(type='product')
    groups = ProductGroup.objects.all()

    page = request.GET.get('page')
    paginator = Paginator(all_products, 50)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, "products/index.html", {
        'products': products,
        'tags': tags,
        'groups': groups,
        'title': title
        })

def edit(request, product_id=0, code=None):
    form = ProductForm()
    result = {}

    if int(product_id) > 0:
        result = {}
        product = Product.objects.get(pk=product_id)
        form = ProductForm(instance=product)
        product_id = product.id
    
    if code:
    	gsx = GsxAccount.default()
    	result = gsx.parts_lookup(code)
        product = Product.from_gsx(result[0])
        form = ProductForm(instance=product)
    
    return render(request, 'products/form.html', {'form': form,
        'product_id': product_id,
        'gsx_data': result
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

    if data.get('amount_stocked'):
        product.amount_stocked(data.get('amount_stocked'))
    
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
    data = Invoice.objects.all()
    return render(request, 'store/invoices.html', {'invoices': data})
  
def create_po(request, product_id=None, order_id=None):
    """
    Create a new Purchase Order
    """
    po = PurchaseOrder.objects.create(created_by=request.user)

    if order_id:
        po.sales_order = order_id
        po.save()

        for i in ServiceOrderItem.objects.filter(order_id=order_id):
            product = Product.objects.get(pk=i.product_id)
            po.add_product(product)

    if product_id:
        product = Product.objects.get(pk=product_id)
        PurchaseOrderItem.objects.create(code=product.code,
            quantity=1,
            purchase_order=po,
            product_id=product.id, 
            price=product.price_purchase)

    messages.add_message(request, messages.INFO,
        _(u'Ostotilaus %d luotu' % po.id))

    return redirect(po)

def edit_po(request, id, item_id=None, action='add'):
    po = PurchaseOrder.objects.get(pk=id)
    form = PurchaseOrderForm(instance=po)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=po)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO,
                _(u'Ostotilaus tallennettu'))

            items = request.POST.getlist('items')
            prices = request.POST.getlist('prices')
            amounts = request.POST.getlist('amounts')
            
            for k, v in enumerate(items):
                d = dict(amount=amounts[k], price=prices[k])
                item = PurchaseOrderItem.objects.get(pk=v)
                f = PurchaseOrderItemForm(d, instance=item)
                f.save()

            return redirect('servo.views.products.index_po')

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
    return redirect('servo.views.products.index_po')
  
def index_po(request):
    data = PurchaseOrder.objects.all()
    return render(request, 'products/purchase_orders.html', {'orders': data})

def order_stock(request, po_id):
    po = PurchaseOrder.objects.get(pk=po_id)
    gsx = GsxAccount.default()
    items = []
    for i in po.purchaseorderitem_set.all():
        items.append({'partNumber': i.code, 'quantity': "1"})

    so = gsx.create_stocking_order(purchaseOrderNumber=str(po.id),
        shipToCode="677592",
        orderLines=items)
    print so

    return HttpResponse(po)

def remove_po(request, po_id):
    pass

def index_incoming(request, shipment=None, date=None):
    if request.method == 'POST':
        for i in request.POST.getlist('items'):
            inv = Inventory.objects.get(pk=i)


    inventory = Inventory.objects.filter(kind="po")
    return render(request, 'products/index_incoming.html',
        {'inventory': inventory})
  
def index_outgoing(request, shipment=None, date=None):
    pass
