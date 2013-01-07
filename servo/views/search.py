#coding=utf-8

import re
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import DotExpandedDict

import json, cPickle as pickle

from servo.lib.gsxlib.gsxlib import Gsx, looks_like
from servo.models.common import *
from servo.models.order import *
from servo.models.note import *

def gsx(request, what):
    results = []
    #results = cache.get('%s-%s' % (what, value))
    results = False

    if not results:
        gsx = GsxAccount.default()
        query = request.GET.get('serialNumber')

        if what == 'warranty':
            result = gsx.warranty_status(query)[0]

            if re.match('iPhone', result.get('productDescription')):
                ad = gsx.fetch_ios_activation(serialNumber=query)
                result['activationDetails'] = ad[0]

            results = [result]

        if what == 'parts':
            if not query:
                query = request.GET.get('partNumber')

            results = gsx.parts_lookup(query)

        if what == 'repairs':
            if query:
                results = gsx.repair_lookup(serialNumber=query)
            else:
                what = 'repair_details'
                results = gsx.repair_details(request.GET['dispatchId'])

        # Cache the results for quicker quicker access later
        cache.set('%s-%s' %(what, query), results)

    return render(request, 'search/results-%s.html' % what, {
        'results': results,
        'query': query
        })

def spotlight(request, what='warranty'):
    """
    Search for anything
    GSX searches are done separately
    """
    results = dict()
    query = request.GET.get('q')
    
    results['gsx'] = looks_like(query)
    
    if results['gsx'] == 'dispatchId':
        what = 'repairs'

    if results['gsx'] == 'partNumber':
        what = 'parts'

    if Order.objects.filter(code=query).exists():
        order = Order.objects.get(code=query)
        return redirect('/orders/%d/' % order.id)

    results['what'] = what
    results['query'] = query
    results['devices'] = Device.objects.filter(sn__icontains=query)

    results['orders'] = Order.objects.filter(customer__name__icontains=query)

    if looks_like(query) == 'serialNumber':
        results['orders'] = Order.objects.filter(devices__sn__contains=query)

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
