from servo3.models import Product, PurchaseOrder, Invoice, Inventory
from bson.objectid import ObjectId
from django.shortcuts import render
from django.http import HttpResponse

def save_po(req):
  po = PurchaseOrder()
  
  for k, v in req.POST.items():
    po.__setattr__(k, v)
  
  codes = req.POST.getlist("code")
  titles = req.POST.getlist("title")
  amounts = req.POST.getlist("amount")
  prices = req.POST.getlist("price")
  
  po.save()
  
  for k, v in enumerate(codes):
    amt = int(amounts[k])
    price = float(prices[k])
    product = Product.objects(code = v).first()
    po.products.append({"code": v, "title": titles[k], "amount": amt, "price": price})
    
    for i in xrange(amt):
      i = Inventory(slot = po, product = product)
      i.save()
  
  po.save()
  return HttpResponse('Ostotilaus tallennettu')
  
def edit_po(req, id):
  """docstring for edit_po"""
  pass

def order_products(req, ids):
  products = []
  
  for i in ids.strip(";").split(";"):
    products.append(Product.objects(number = int(i)).first())
  
  return render(req, "store/purchase_order.html", {"products": products})
  
def sell_product(req):
  pass
  
def index_po(req):
  data = PurchaseOrder.objects().all()
  return render(req, 'store/index_po.html', {"orders": data})
  
def index_incoming(req, shipment = None, date = None):
  products = 
  
def index_outgoing(req, shipment = None, date = None):
  pass
  
  