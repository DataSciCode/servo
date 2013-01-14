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

def remove(request, id):
    if 'id' in request.POST:
        dev = Device.objects.get(pk=request.POST['id'])
        dev.delete()
        messages.add_message(request, messages.INFO, _(u'Laite poistettu'))
        return redirect('/devices/')
    else:
        dev = Device.objects.get(pk=id)
        return render(request, "devices/remove.html", {'device': dev})

def edit(request, device_id=None):
    if request.method == 'POST':
        return save(request, device_id)

    if device_id:
        dev = Device.objects.get(pk=device_id)
        form = DeviceForm(instance=dev)
    else:
        form = DeviceForm()

    return render(request, 'devices/form.html', {'form': form})

def view(request, device_id):
    device = Device.objects.get(pk=device_id)
    return render(request, 'devices/view.html', {'device': device})

def save(request, device_id):

    if device_id:
        device = Device.objects.get(pk=device_id)
    else:
        device = Device()

    form = DeviceForm(request.POST, instance=device)
    
    if form.is_valid():
        device = form.save()
        messages.add_message(request, messages.INFO, _(u'Laite tallennettu'))
        return redirect('/devices/')

    return render(request, 'devices/form.html', {'form': form})

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
