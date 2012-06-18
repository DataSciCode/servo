from servo.models import *

from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime

from django.utils.datastructures import DotExpandedDict

def invoices(req):
  data = Invoice.objects.all()
  return render(req, "store/invoices.html", {"invoices": data})

def dispatch(req, order_id = None, numbers = None):
  products = []

  if req.method == "POST":
    data = DotExpandedDict(req.POST)
    #print data
    invoice = Invoice(payment_method=data['payment_method'],
      total_payable=float(data['total']))

    if "paid" in data:
      invoice.paid_at = datetime.now()

    products = data.get("products")

    if "customer" in data:
      customer = Customer.objects.with_id(ObjectId(data['customer']))
      invoice.customer = customer.asdict()

    for k in products:
      invoice.products.append(products[k])
    
    invoice.save()

    return HttpResponse("Tuotteet toimitettu")

  total = 0

  if order_id:
    order = Order.objects.with_id(ObjectId(order_id))
    total = order.total
    products = order.products

  if numbers:
    totals = {}
    totals['amount'] = 0
    totals['notax'] = 0
    totals['tax'] = 0
    totals['sum'] = 0

    for p in numbers.rstrip(";").split(";"): # http://store/blaa/45;234;123;
      product = Product.objects(number = int(p)).first()
      totals['amount'] += 1
      totals['notax'] += product.price_notax
      totals['tax'] += product.tax()
      totals['sum'] += product.price_sales
      
      oi = OrderItem(product = product, price = product.price_sales, amount = 1)
      products.append(oi)

  return render(req, "store/dispatch.html", {"products": products, "totals": totals})

def save_po(req):

  po = PurchaseOrder()
  
  for k, v in req.POST.items():
    po.__setattr__(k, v)
  
  codes = req.POST.getlist("code")
  titles = req.POST.getlist("title")
  prices = req.POST.getlist("price")
  amounts = req.POST.getlist("amount")
  
  po.save()
  
  for k, v in enumerate(codes):
    amt = int(amounts[k])
    price = float(prices[k])
    product = Product.objects(code = v).first()
    po.products.append({"code": v, "title": titles[k], "amount": amt, "price": price})
    
    for i in xrange(amt):
      i = Inventory(slot = po, product = product, kind = "po")
      i.save()
  
  po.save()

  return HttpResponse('Ostotilaus tallennettu')
  
def edit_po(req, id):
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
  inventory = Inventory.objects(kind = "po").all()
  return render(req, "store/index_incoming.html", {"inventory": inventory})
  
def index_outgoing(req, shipment = None, date = None):
  pass
  