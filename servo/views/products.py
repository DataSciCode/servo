from servo.models import *
from django.shortcuts import render
from django.http import HttpResponse
import json

from django.forms import ModelForm

class ProductForm(ModelForm):
    class Meta:
        model = Product

def create(req, order_id=None):
    p = Product()
    return render(req, "products/form.html", {'product': p})

def index(req):
    req.session['order'] = None
    data = Product.objects.all()
    tags = Tag.objects.filter(type='product')

    return render(req, 'products/index.html', {'data': data, 'tags': tags})

def edit(req, id):
    try:
        product = Product.objects.get(pk = id)
    except Exception, e:
        gsx_data = req.session.get('gsx_data')

        if id in gsx_data:
            result = gsx_data.get(id)
            conf = Configuration.objects.get(pk = 1)

            ep = float(result.get('exchangePrice'))
            sp = float(result.get('stockPrice'))
            
            ep = ep+(ep/100*conf.pct_margin)+(ep/100*conf.pct_vat)
            sp = sp+(sp/100*conf.pct_margin)

            product = Product(code = result.get('partNumber'),
                title = result.get('partDescription'),
                price_purchase = result.get('stockPrice'),
                price_exchange = ep,
                pct_margin = conf.pct_margin,
                pct_vat = conf.pct_vat,
                price_notax = sp,
                price_sales = sp+(sp/100*conf.pct_vat))
            #product.gsx_data = json.dumps(result)

    if req.session.get("order"):
        product.sn = "asd"
        product.amount_sold = 1
  
    return render(req, "products/form.html", {'product': product})
  
def remove(req, id = None, idx = None):
    if idx:
        idx = int(idx)
        order_id = req.session.get("order").id
        Order.objects(id=order_id).update_one(pop__products=idx)
        return HttpResponse("Tuote poistettu tilauksesta")

    if 'id' in req.POST:
        product = Product.objects.get(pk = req.POST['id']);
        Inventory.objects.filter(product = product).delete()
        product.delete()
        return HttpResponse("Tuote poistettu")
    else:
        product = Product.objects.get(pk = id)

    return render(req, 'products/remove.html', {'product': product})

def save(req):
    if 'id' in req.POST:
        product = Product.objects.get(pk = req.POST['id'])
        form = ProductForm(instance=product)
    else:
        form = ProductForm(req.POST)

    if form.is_valid():
        form.save()
    else:
        print form.errors

    return HttpResponse("Tuote tallennettu")
    data = form.cleaned_data
    print data
    
    if req.session.get('gsx_data'):
        if product.code in req.session.get('gsx_data'):
            product.gsx_data = req.session['gsx_data'].get(product.code)
  
    product.save()
    
    product.tags = req.POST.getlist('tags')

    if req.POST.get("amount_stocked"):
        product.amount_stocked(req.POST.get("amount_stocked"))
    
    for a in req.POST.getlist("attachments"):
        doc = Attachment.objects(id = ObjectId(a)).first()
        product.attachments.append(doc)
  
    if req.session['order']:
        amount = int(req.POST.get("amount_sold"))
        oi = OrderItem(product = product, sn = req.POST.get("sn"),
            price = req.POST.get("price_sales"),
            amount = amount)
        order = Order.objects(id=req.session['order'].id).update_one(push__products=oi)
        req.session['order'] = order
    
    return HttpResponse("Tuote tallennettu")
  
def search(req):
    return render(req, "products/search.html")
  
def reserve(req, order_id = None):
    if req.method == "POST":
        order = Order.objects(id=ObjectId(req.POST['id'])).first()
        Inventory.objects(slot=order).delete()
    
        for p in order.products:
            i = Inventory(slot=order, product=p.product, sn=p.sn, kind="order")
            i.save()
    
        Event(description = "Tilauksen tuotteet varattu", ref_order = order,
            type = "products_reserved").save()
        return HttpResponse("Tuotteet varattu")
    else:
        order = Order.objects(id = ObjectId(order_id)).first()
        return render(req, "products/reserve.html", order)
