from servo.models import *
from django.shortcuts import render
from django.http import HttpResponse
import json
from django import forms

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
    return render(req, 'products/form.html', {'form': form})

def index(req):
    req.session['order'] = None
    data = Product.objects.all()
    tags = Tag.objects.filter(type='product')

    return render(req, 'products/index.html', {'data': data, 'tags': tags})

def edit(req, id):
    try:
        product = Product.objects.get(pk=id)
        form = ProductForm(instance = product)
    except Exception, e:
        gsx_data = req.session.get('gsx_data')

        if id in gsx_data:
            result = gsx_data.get(id)
            conf = Configuration.objects.get(pk=1)

            ep = float(result.get('exchangePrice'))
            sp = float(result.get('stockPrice'))
            
            ep = ep+(ep/100*conf.pct_margin)+(ep/100*conf.pct_vat)
            sp = sp+(sp/100*conf.pct_margin)

            form = ProductForm({
                'code': result.get('partNumber'),
                'title': result.get('partDescription'),
                'price_purchase': result.get('stockPrice'),
                'price_exchange': ep,
                'pct_margin': conf.pct_margin,
                'pct_vat': conf.pct_vat,
                'price_notax': sp,
                'price_sales': sp+(sp/100*conf.pct_vat)
            })
            #product.gsx_data = json.dumps(result)
    
    return render(req, 'products/form.html', {'form': form,
        'product': product})

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
    if id:
        product = Product.objects.get(pk=id)
        form = ProductForm(req.POST, instance=product)
    else:
        form = ProductForm(req.POST)

    if not form.is_valid():
        print form.errors
        return HttpResponse(form.errors)

    form.save()
    data = form.cleaned_data

    try:
        if data['code'] in req.session.get('gsx_data'):
            gsx_data = json.dumps(req.session['gsx_data'].get(data.code))
            product.gsx_data = gsx_data
    except Exception, e:
        pass

    #product.tags = req.POST.getlist('tags')

    if req.POST.get('amount_stocked'):
        pass
        #product.amount_stocked(req.POST.get('amount_stocked'))
    
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
        
        Event.objects.create(description = 'Tilauksen tuotteet varattu',
            order = order,
            type = 'products_reserved',
            user = req.session.get('user'))
        return HttpResponse('Tuotteet varattu')
    else:
        order = Order.objects.get(pk = order_id)
        return render(req, 'products/reserve.html', {'order': order})
