from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.datastructures import DotExpandedDict
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django import forms
from django.contrib import messages
from django.core.cache import cache

from servo.models import Tag
from devices.models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        exclude = ('spec', 'customers', )
    
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.filter(type='device'),
        required=False)

def index(request, *args, **kwargs):
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

    return render(request, "devices/index.html", {
        'devices': devices,
        'tags': tags
        })

def create(request):
	return render(request, "devices/form.html", {'form': DeviceForm()})

def remove(req, id):
    if 'id' in req.POST:
        dev = Device.objects.get(pk=req.POST['id'])
        dev.delete()
        messages.add_message(req, messages.INFO, _(u'Laite poistettu'))
        return redirect('/devices/')
    else:
        dev = Device.objects.get(pk=id)
        return render(req, 'devices/remove.html', {'device': dev})

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
    return render(req, 'devices/form.html', {'device': dev,
        'form': form, 'gsx_data': gsx_data})

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
        messages.add_message(request, messages.INFO, _(u'Laite tallennettu'))
        return redirect('/devices/')

    return render(request, 'devices/form.html', {'form': form, 'device': device})

def search(req, query):
    if query:
        return render(req, 'search_results.html')

    return render(req, 'devices/earch.html')

def edit_spec(req, spec_id=None):
    if req.method == 'POST':
        form = SpecForm(req.POST)
        if 'id' in req.POST:
            spec = Spec.objects.get(pk=req.POST['id'])
            form = SpecForm(req.POST, instance=spec)
        if form.is_valid():
            form.save()
            messages.add_message(req, messages.INFO, u'Malli tallennettu')
            return redirect('/devices/specs/')
    else:
        form = SpecForm()
        if spec_id:
            spec = Spec.objects.get(pk=spec_id)
            form = SpecForm(instance=spec)

    specs = Spec.objects.all()

    return render(req, 'devices/spec_form.html', {
        'form': form,
        'specs': specs
        })

def view_spec(req, spec_id):
    specs = Spec.objects.all()
    return render(req, 'devices/view_spec.html', {'specs': specs})
