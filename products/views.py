from django.shortcuts import render
from django.http import HttpResponse
from servo3.models import *
from bson.objectid import ObjectId

def create(req, order_id=None):
  p = Product()
  return render(req, 'products/form.html', {'product': p})

def index(req):
  data = Product.objects
  return render(req, 'products/index.html', {'data': data})
  
def edit(req, id):
  
  if id in req.session.get('gsx_data'):
    conf = Config.objects.first()
    result = req.session['gsx_data'].get(id)
    product = Product(code = result.get('partNumber'),\
      title = result.get('partDescription'), gsx_data = result,\
      price_purchase = result.get('stockPrice'),\
      price_exchange = result.get('exchangePrice'),\
      pct_margin = conf.pct_margin, pct_vat = conf.pct_vat,\
      price_notax = result.get('stockPrice'),\
      price_sales = result.get('stockPrice'))
  else:
    product = Product.objects(id = ObjectId(id)).first()
  
  return render(req, 'products/form.html', {'product': product})
  
def remove(req, id = None):
  if 'id' in req.POST:
    product = Product.objects.with_id(ObjectId(req.POST['id']));
    Inventory.objects(product = product).delete()
    product.delete()
    return HttpResponse('Tuote poistettu')
  else:
    product = Product.objects(id = ObjectId(id)).first()
    return render(req, 'products/remove.html', product)
  
def save(req):
  product = Product()
  
  if 'id' in req.POST:
    product = Product.objects(id = ObjectId(req.POST['id'])).first()
  
  for k, v in req.POST.items():
    product.__setattr__(k, v)
  
  product.tags = req.POST.getlist('tags')
  
  for a in req.POST.getlist("attachments"):
    doc = Attachment.objects(id = ObjectId(a)).first()
    #product.attachments = [doc]
  
  product.save()
  
  amount_stocked = int(req.POST['amount_stocked'])
  Inventory.objects(slot = product).delete()
  
  for _ in xrange(amount_stocked):
    i = Inventory(slot = product, product = product)
    i.save()
  
  """
  if req.session['order']:
    oi = OrderItem(product)
    req.session['order'].products.append(oi)
    req.session['order'].save()
  """
  return HttpResponse('Tuote tallennettu')
  
def search(req):
  return render(req, 'products/search.html')
  