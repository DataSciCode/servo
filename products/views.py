from django.shortcuts import render
from django.http import HttpResponse
from servo3.models import Product, Config
from bson.objectid import ObjectId

def create(req, order_id=None):
  p = Product()
  return render(req, 'products/form.html', p)

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
    product = Product.objects(id = ObjectId(req.POST['id']))
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
  
  product.save()
  return HttpResponse('Tuote tallennettu')
  
def search(req):
  return render(req, 'products/search.html')
  