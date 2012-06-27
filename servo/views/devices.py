from servo.models import Device, Order, Spec
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.datastructures import DotExpandedDict
from django import forms

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device

def index(req):
    devices = Device.objects.all()
    return render(req, 'devices/index.html', {'devices': devices})
  
def create(req, order=None, customer=None):
    device = Device()
    form = DeviceForm()
    if order:
        req.session['order'] = Order.objects.get(pk=order)
    
    return render(req, 'devices/form.html', {'device': device, 'form': form})
  
def remove(req, id = None):
    if 'id' in req.POST:
        dev = Device.objects.get(pk=req.POST['id'])
        dev.delete()
        return HttpResponse('Laite poistettu')
    else:
        dev = Device.objects.get(pk=id)
        return render(req, 'devices/remove.html', {'device': dev})

def edit(req, id):
    if id in req.session.get('gsx_data'):
        import json
        result = req.session['gsx_data'].get(id)
        dev = Device(sn=result.get('serialNumber'),\
            description=result.get('productDescription'),
            purchased_on=result.get('estimatedPurchaseDate'))
    else:
        dev = Device.objects.get(pk=id)
    
    form = DeviceForm(instance=dev)
    return render(req, 'devices/form.html', {'device': dev, 'form': form})

def save(req):

    if 'id' in req.POST:
        # search by SN to avoid duplicates
        dev = Device.objects.get(sn=req.POST['sn'])
    else:
        dev = Device()
    
    for k, v in data.items():
        dev.__setattr__(k, v)
    
    # make sure we have this spec
    spec, created = Spec.objects.get_or_create(title=dev.description)
    dev.spec = spec

    dev.save()

    if req.session['order']:
        order = Order.objects.get(pk=req.session['order'].id)
        order.devices.add(dev)
        req.session['order'] = order

    return HttpResponse('Laite tallennettu')

def search(req):
    return render(req, 'devices/search.html')
