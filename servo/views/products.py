from django.shortcuts import render
from django.http import HttpResponse
import json
from django import forms
from servo.models import *
from decimal import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

    amount_ordered = forms.CharField(max_length=3,
        widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    amount_reserved = forms.CharField(max_length=3,
        widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    amount_stocked = forms.CharField(max_length=3, required=False)

def create(req, order_id=None):
    p = Product()
    form = ProductForm()
    id = 0
    return render(req, 'products/form.html', {'form': form, 'id': id})

def index(req):
    req.session['order'] = None
    data = Product.objects.all()
    tags = Tag.objects.filter(kind='product')

    return render(req, 'products/index.html', {'data': data, 'tags': tags})

def edit(req, id=0):
    try:
        result = {}
        product = Product.objects.get(pk=id)
        form = ProductForm(instance=product)
        id = product.id
    except Exception, e:
        gsx_data = req.session.get('gsx_data')

        if id in gsx_data:
            result = gsx_data.get(id)
            print result
            conf = Configuration.objects.get(pk=1)

            getcontext().rounding = ROUND_UP

            sp = Decimal(result.get('stockPrice'))
            ep = Decimal(result.get('exchangePrice'))
            
            sp = (sp+(sp/100*conf.pct_margin)).quantize(Decimal('1.'))
            ep = (ep+(ep/100*conf.pct_margin)+(ep/100*conf.pct_vat)).quantize(Decimal('1.'))

            product = Product(code=result.get('partNumber'),
                title=result.get('partDescription'),
                price_purchase=result.get('stockPrice'),
                price_exchange=ep,
                pct_margin=conf.pct_margin,
                pct_vat=conf.pct_vat,
                price_notax=sp,
                price_sales=sp+(sp/100*conf.pct_vat).quantize(Decimal('1.'))
            )

            form = ProductForm(instance=product)
    
    return render(req, 'products/form.html', {'form': form,
        'product': product, 'gsx_data': result, 'id': id})

def remove(req, id=None, order_item_id=None):
    if order_item_id:
        oi = OrderItem.objects.get(pk=order_item_id).delete()
        return HttpResponse('Tuote poistettu tilauksesta')

    if 'id' in req.POST:
        product = Product.objects.get(pk=req.POST['id']);
        Inventory.objects.filter(product=product).delete()
        product.delete()
        return HttpResponse('Tuote poistettu')
    else:
        product = Product.objects.get(pk=id)

    return render(req, 'products/remove.html', {'product': product})

def save(req, id=None):
    try:
        product = Product.objects.get(pk=id)
        form = ProductForm(req.POST, instance=product)
    except Exception, e:
        product = Product()
        form = ProductForm(req.POST)
        
    if not form.is_valid():
        return HttpResponse(str(form.errors), status=500)
        
    product = form.save()

    try:
        if product.code in req.session.get('gsx_data'):
            gsx_data = req.session['gsx_data'].get(product.code)
            for k, v in gsx_data.items():
                GsxData.objects.create(key=k, value=v,
                    references="product", reference_id=product.id)
    except Exception, e:
        print form.errors

    #product.tags = req.POST.getlist('tags')

    if req.POST.get('amount_stocked'):
        product.amount_stocked(data.get('amount_stocked'))
    
    for a in req.POST.getlist('attachments'):
        doc = Attachment.objects.get(pk=a)
        product.attachments.add(doc)
    
    if req.session['order']:
        oi = OrderItem(product=product,
            sn=req.POST.get('sn', ''),
            price=req.POST.get('price_sales'),
            order=req.session['order'])
        oi.save()
        req.session['order'] = req.session['order']
    
    return HttpResponse('Tuote tallennettu')
    
def search(req):
    return render(req, 'products/search.html')

def reserve(req, order_id=None):
    if req.method == 'POST':
        oid = req.POST['id']
        order = Order.objects.get(pk = oid)
        Inventory.objects.filter(slot = oid).delete()
        
        for p in order.products.all():
            i = Inventory.objects.create(slot=oid, product=p, kind='order')
        
        Event.objects.create(description='Tilauksen tuotteet varattu',
            order = order,
            type = 'products_reserved',
            user = req.session.get('user'))
        return HttpResponse('Tuotteet varattu')
    else:
        order = Order.objects.get(pk = order_id)
        return render(req, 'products/reserve.html', {'order': order})
