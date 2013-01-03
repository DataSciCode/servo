from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.datastructures import DotExpandedDict
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django import forms
from django.contrib import messages
from django.core.cache import cache

from servo.models.common import Tag
from servo.models.device import Device
from servo.models.product import Product

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ('spec', 'customers', 'files', )
    
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type='device'),
        required=False)

def index(request, *args, **kwargs):
    title = _(u'Kaikki')
    
    if 'query' in kwargs:
        all_devices = Device.objects.filter(sn=kwargs['query'])
    else:
        all_devices = Device.objects.all()

    if 'tag' in kwargs:
        all_devices = Device.objects.filter(tags=kwargs['tag'])

    page = request.GET.get('page')
    paginator = Paginator(all_devices, 50)

    try:
        devices = paginator.page(page)
    except PageNotAnInteger:
        devices = paginator.page(1)
    except EmptyPage:
        devices = paginator.page(paginator.num_pages)

    tags = Tag.objects.filter(type='device')
    
    return render(request, 'devices/index.html', {
        'devices': devices,
        'tags': tags,
        'title': title,
        })

def create(request):
	return render(request, 'devices/form.html', {'form': DeviceForm()})

def remove(request, id):
    if 'id' in request.POST:
        dev = Device.objects.get(pk=request.POST['id'])
        dev.delete()
        messages.add_message(request, messages.INFO, _(u'Laite poistettu'))
        return redirect('/devices/')
    else:
        dev = Device.objects.get(pk=id)
        return render(request, "devices/remove.html", {'device': dev})

def edit(req, id):
    gsx_data = {}

    #if id in req.session.get('gsx_data'):
    #    import json
    #    result = req.session['gsx_data'].get(id)
    #    dev = Device(sn=result.get('serialNumber'),\
    #        description=result.get('productDescription'),
    #        purchased_on=result.get('estimatedPurchaseDate'))
    #    gsx_data = result
    #else:
    dev = Device.objects.get(pk=id)
    
    form = DeviceForm(instance=dev)
    return render(req, 'devices/form.html', {'device': dev, 'form': form, 
    	'gsx_data': gsx_data})

def view(request, id):
    device = Device.objects.get(pk=id)
    return render(request, 'devices/view.html', {'device': device})

@require_POST
def save(request, id):
    if request.method == 'POST':
        # search by SN to avoid duplicates
        device = Device.objects.get(sn=request.POST['sn'])
        form = DeviceForm(request.POST, instance=device)
    else:
        form = DeviceForm(request.POST)
    
    if form.is_valid():
        device = form.save()
        messages.add_message(request, messages.INFO, _(u"Laite tallennettu"))
        return redirect('/devices/')

    return render(request, "devices/form.html", {'form': form, 'device': device})

def search(request, query):
    if query:
        return render(request, "search_results.html")

    return render(request, "devices/search.html")

def parts(request, device_id):
	device = Device.objects.get(pk=device_id)
	device.parts = Product.objects.filter(tags__pk=device.spec_id)
	return render(request, "devices/parts.html", {'device': device})

def choose(request, order_id):
    #request.session['current_order'] = Order.objects
    messages.add_message(request, message.INFO, _(u'Valitse laite'))
    return index(request)
