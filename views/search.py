from servo3.models import Device, Product, Customer
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def lookup(req, what):
    from gsx.views import parts_lookup, looks_like, warranty_status
  
    results = []
    action = "edit"
    collection = "device"
  
    query = req.POST.get('q')
  
    if what == "product-local":
        collection = "products"
        products = Product.objects(code__istartswith = query)
        for r in products:
            results.append({'id': r.id, 'title': r.code, 'description': r.title})
  
    if what == "product-gsx":
        collection = "products"
        param = looks_like(query)
        req.session['gsx_data'] = {}
    
    if param == "partNumber":
        for r in parts_lookup(query):
            req.session['gsx_data'] = {r.get('partNumber'): r}
            results.append({'id': r['partNumber'], 'title': r['partNumber'],\
                'description': r['partDescription']})
    
    if req.session.get('order'):
        try:
            sn = req.session['order']['devices'][0].sn
            if looks_like(sn, "serialNumber"):
                query = {"serialNumber": sn, "partDescription": query}

            for r in parts_lookup(query):
                pn = r.get('partNumber')
                req.session['gsx_data'][pn] = r
                results.append({'id': r['partNumber'],\
                    'title': r['partNumber'],\
                    'description': r['partDescription']})
        except Exception, e:
            pass
    
    print query
    
  if what == "device-local":
    local = Device.objects(sn__istartswith = query)
    for d in local:
      results.append({'id': d.id, 'title': d.sn, 'description': d.description})
    
  if what == "device-gsx":
    for r in warranty_status(query):
      req.session['gsx_data'] = {query: r}
      results.append({'title': r.get('productDescription'),
        'description': r.get('configDescription'), 'id': query})
  
  if what == "customer":
    collection = "customer"
    customers = Customer.objects(name__istartswith = query)
    
    for r in customers:
      results.append({'id': r.id, 'title': r.name})
  
  return render(req, 'search/lookup.html', {'results': results,\
    'action': action, 'collection': collection})
  