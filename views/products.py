from servo3.models import *
from bson.objectid import ObjectId

from django.shortcuts import render
from django.http import HttpResponse

def create(req, order_id=None):
  p = Product()
  return render(req, "products/form.html", {"product": p})

def index(req):
  req.session['order'] = None
  data = Product.objects.all()
  tags = Tag.objects(type = "product").all()

  return render(req, "products/index.html", {"data": data, "tags": tags})
  
def edit(req, id):
  if id in req.session.get('gsx_data'):
    conf = Configuration.objects.first()
    result = req.session['gsx_data'].get(id)
    product = Product(code = result.get('partNumber'),
      title = result.get('partDescription'),
      gsx_data = result,
      price_purchase = result.get('stockPrice'),
      price_exchange = result.get('exchangePrice'),
      pct_margin = conf.pct_margin,
      pct_vat = conf.pct_vat,
      price_notax = result.get('stockPrice'),
      price_sales = result.get('stockPrice'))
  else:
    product = Product.objects(id = ObjectId(id)).first()
  
  if req.session.get("order"):
    product.sn = "asd"
    product.amount_sold = 1
  
  return render(req, "products/form.html", {"product": product})
  
def remove(req, id = None, idx = None):
  if idx:
    idx = int(idx)
    order_id = req.session.get("order").id
    Order.objects(id=order_id).update_one(pop__products=idx)
    return HttpResponse("Tuote poistettu tilauksesta")

  if 'id' in req.POST:
    product = Product.objects.with_id(ObjectId(req.POST['id']));
    Inventory.objects(product = product).delete()
    product.delete()
    return HttpResponse("Tuote poistettu")
  else:
    product = Product.objects(id = ObjectId(id)).first()
    return render(req, "products/remove.html", product)
  
def save(req):
  product = Product()
  
  if "id" in req.POST:
    product = Product.objects(id = ObjectId(req.POST['id'])).first()
  
  product.code = req.POST.get("code").upper()
  product.title = req.POST.get("title")
  product.tags = req.POST.getlist('tags')
  product.description = req.POST.get("description")
  product.pct_vat = float(req.POST.get("pct_vat", 0))
  product.pct_margin = float(req.POST.get("pct_margin", 0))
  
  product.is_serialized = "is_serialized" in req.POST
  
  product.warranty_period = req.POST.get("warranty_period")

  product.price_notax = float(req.POST.get("price_notax", 0))
  product.price_sales = float(req.POST.get("price_sales", 0))
  product.price_exchange = float(req.POST.get("price_exchange", 0))
  product.price_purchase = float(req.POST.get("price_purchase", 0))
  
  if product.code in req.session.get('gsx_data'):
    product.gsx_data = req.session['gsx_data'].get(product.code)
  
  product.save()
  
  if req.POST.get("amount_stocked"):
    product.amount_stocked(req.POST.get("amount_stocked"))
  
  for a in req.POST.getlist("attachments"):
    doc = Attachment.objects(id = ObjectId(a)).first()
    product.attachments.append(doc)
  
  if req.session['order']:
    amount = int(req.POST.get("amount_sold"))
    oi = OrderItem(product = product, sn = req.POST.get("sn"),
      price = req.POST.get("price_sales"), amount = amount)
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
  