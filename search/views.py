from servo3.models import Device, Product
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def lookup(req, what):
  """docstring for lookup"""
  results = []
  action = "edit"
  collection = "device"
  
  query = req.POST.get('q')
  
  if what == "product-local":
    collection = "products"
    results = Product.objects
  
  if what == "product-gsx":
    collection = "products"
    from gsx.views import parts_lookup
    
    for r in parts_lookup(query):
      req.session['gsx_data'] = {r.get('partNumber'): r}
      results.append({'id': r['partNumber'], 'title': r['partNumber'], 'description': r['partDescription']})
    
  if what == "device-local":
    local = Device.objects(sn = query)
    for d in local:
      results.append({'id': d.id, 'title': d.sn, 'description': d.description})
    
  if what == "device-gsx":
    from gsx.views import warranty_status
    gsx_results = [warranty_status(query)]
    
    for r in gsx_results:
      req.session['gsx_data'] = {r.get('serialNumber'): r}
      results.append({'title': r.get('productDescription'), \
      'description': r.get('configDescription'), 'id': r.get('serialNumber')})
  
  return render(req, 'search/lookup.html', {'results': results,\
    'action': action, 'collection': collection})
  