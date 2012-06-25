from gsxlib.gsxlib import Gsx
from servo.models import Device, Product, Customer, GsxAccount, Search
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import DotExpandedDict
import json

@csrf_exempt
def save(req):
    query = DotExpandedDict(req.POST)
    title = req.POST.get('title', '')
    model = req.POST.get('model')
    query = json.dumps(query['query'])
    Search.objects.create(query = query, title = title, model = model)

@csrf_exempt
def lookup(req, what):
    results = []
    action = 'edit'
    collection = 'device'

    query = req.POST.get('q')

    if what == 'customer':
        collection = 'customer'
        customers = Customer.objects.filter(name__istartswith = query)
    
        for r in customers:
            results.append({'id': r.id, 'title': r.fullname})

        return render(req, 'search/lookup.html', {'results': results,\
            'action': action, 'collection': collection})

    if what == 'product-local':
        collection = 'products'
        products = Product.objects.filter(code__istartswith = query)
        for r in products:
            results.append({'id': r.id, 'title': r.code, 'description': r.title})

        return render(req, 'search/lookup.html', {'results': results,\
            'action': action, 'collection': collection})
    
    if what == 'device-local':
        local = Device.objects.filter(sn__istartswith = query)
        for d in local:
            results.append({'id': d.id, 'title': d.sn, 'description': d.description})

        return render(req, 'search/lookup.html', {'results': results,\
            'action': action, 'collection': collection})

    # @todo Use the order's queue's GSX account, then revert to default
    act = GsxAccount.objects.get(is_default = True)
    gsx = Gsx(act.sold_to, act.username, act.password)

    param = gsx.looks_like(query)
    
    if what == 'product-gsx':
        collection = 'products'
        req.session['gsx_data'] = {}
        
        if param == 'partNumber':
            for r in gsx.parts_lookup(query):
                req.session['gsx_data'] = {r.get('partNumber'): r}
                results.append({'id': r['partNumber'], 'title': r['partNumber'],\
                    'description': r['partDescription']})
    
        if req.session.get('order'):
            try:
                sn = req.session['order']['devices'][0].sn
                if gsx.looks_like(sn, 'serialNumber'):
                    query = {'serialNumber': sn, 'partDescription': query}

                for r in gsx.parts_lookup(query):
                    pn = r.get('partNumber')
                    req.session['gsx_data'][pn] = r
                    results.append({'id': r['partNumber'],\
                        'title': r['partNumber'],\
                        'description': r['partDescription']})
            except Exception, e:
                pass
    
    if what == 'device-gsx':
        gsx_results = gsx.warranty_status(query)
        
        for r in gsx_results:
            req.session['gsx_data'] = {query: r}
            results.append({'title': r.get('productDescription'),
                'description': r.get('configDescription'), 'id': query})
  
    return render(req, 'search/lookup.html', {'results': results,\
        'action': action, 'collection': collection})
