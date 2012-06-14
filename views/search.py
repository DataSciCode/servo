from servo3.models import Device, Product, Customer, GsxAccount
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from gsxlib.gsxlib import Gsx

@csrf_exempt
def lookup(req, what):
    results = []
    action = "edit"
    collection = "device"
  
    # @todo Use the order's queue's GSX account, then revert to default
    act = GsxAccount.objects(is_default = True).first()
    gsx = Gsx(act.sold_to, act.username, act.password)

    query = req.POST.get('q')
  
    if what == "product-local":
        collection = "products"
        products = Product.objects(code__istartswith = query)
        for r in products:
            results.append({'id': r.id, 'title': r.code, 'description': r.title})
    
    param = gsx.looks_like(query)

    if what == "product-gsx":
        collection = "products"
        req.session['gsx_data'] = {}
    
        if param == "partNumber":
            for r in gsx.parts_lookup(query):
                req.session['gsx_data'] = {r.get('partNumber'): r}
                results.append({'id': r['partNumber'], 'title': r['partNumber'],\
                    'description': r['partDescription']})
    
        if req.session.get('order'):
            try:
                sn = req.session['order']['devices'][0].sn
                if gsx.looks_like(sn, "serialNumber"):
                    query = {"serialNumber": sn, "partDescription": query}

                for r in gsx.parts_lookup(query):
                    pn = r.get('partNumber')
                    req.session['gsx_data'][pn] = r
                    results.append({'id': r['partNumber'],\
                        'title': r['partNumber'],\
                        'description': r['partDescription']})
            except Exception, e:
                pass
    
    if what == "device-local":
        local = Device.objects(sn__istartswith = query)
        for d in local:
            results.append({'id': d.id, 'title': d.sn, 'description': d.description})
    
    if what == "device-gsx":
        gsx_results = gsx.warranty_status(query)
        for r in gsx_results:
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
