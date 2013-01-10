#coding=utf-8

import re
import json
import cPickle as pickle

from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import DotExpandedDict

from servo.lib.gsx import gsx
from servo.models.common import *
from servo.models.order import *
from servo.models.note import *

def search_gsx(request, what):
    """
    Searches for something from GSX
    """
    results = []

    #results = cache.get('%s-%s' % (what, value))

    if not results:
        GsxAccount.default()

        if request.GET.get('serialNumber'):
            query = request.GET.get('serialNumber')
            product = gsx.Product(query)
            
        if what == 'warranty':

            result = product.get_warranty()
            
            if re.match('iPhone', result.productDescription):
                ad = product.get_activation()
                result['activationDetails'] = ad[0]

            results.append(result)

        if what == 'parts':
            if request.GET.get('partNumber'):
                query = request.GET.get('partNumber')
                part = gsx.Part(partNumber=query)
                results.append(part.lookup())
            else:
                results = product.get_parts()

        if what == 'repairs':
            if query:
                try:
                    results = product.get_repairs()
                except Exception, e:
                    return render(request, 'search/results-notfound.html')
            else:
                what = 'repair_details'
                repair = gsx.Repair(dispatchId=request.GET['dispatchId'])
                results = repair.get_details()

        # Cache the results for quicker access later
        cache.set('%s-%s' %(what, query), results)

    return render(request, 'search/results-%s.html' % what, {
        'results': results,
        'query': query
        })

def spotlight(request, what='warranty'):
    """
    Searches for anything
    GSX searches are done separately
    """
    results = dict()
    query = request.GET.get('q')

    if Order.objects.filter(code=query).exists():
        order = Order.objects.get(code=query)
        return redirect(order)

    results['gsx'] = gsx.validate(query)
    
    if results['gsx'] == 'dispatchId':
        what = 'repairs'

    if results['gsx'] == 'partNumber':
        what = 'parts'

    results['what'] = what
    results['query'] = query
    results['devices'] = Device.objects.filter(sn__icontains=query)

    results['orders'] = Order.objects.filter(customer__name__icontains=query)

    if gsx.validate(query, 'serialNumber'):
        results['orders'] = Order.objects.filter(devices__sn__contains=query)

    if gsx.validate(query, 'dispatchId'):
        po = PurchaseOrder.objects.get(confirmation=query)
        results['orders'] = [po.sales_order]

    results['notes'] = Note.objects.filter(body__contains=query)
    results['customers'] = Customer.objects.filter(name__icontains=query)
    results['products'] = Product.objects.filter(code__icontains=query)

    return render(request, 'search/spotlight.html', results)

@csrf_exempt
def save(req):
    data = DotExpandedDict(req.POST)
    title = req.POST.get('title', '')
    model = req.POST.get('model')
    query = {}
    
    for k, v in data['query'].items():
        print k, v
        if v != '':
            query[k] = v

    query = pickle.dumps(query)
    Search.objects.create(query=query, title=title, model=model)
    return HttpResponse('Haku tallennettu')

def remove(req, id):
    Search.objects.get(pk=id).delete()
    return HttpResponse('Haku poistettu')
