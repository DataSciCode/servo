# coding=utf-8
import logging, hashlib
from datetime import datetime
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django import forms

from django.core.cache import cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.datastructures import DotExpandedDict

from django.utils.translation import ugettext as _

from accounts.models import UserProfile
from servo.models import *
from products.models import ProductGroup, Product

class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        exclude = ['statuses']

class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag

class FieldForm(forms.ModelForm):
    class Meta:
        model = Property

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'user_permissions']

    location = forms.ModelChoiceField(queryset=Location.objects.all())
    locale = forms.ChoiceField(UserProfile.LOCALES)

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location

class GsxAccountForm(forms.ModelForm):
    class Meta:
        model = GsxAccount
    
    password = forms.CharField(widget=forms.PasswordInput)

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template

def index(request):
    return render(request, 'admin/index.html')

def documents(request):
    files = Attachment.objects.all()
    return render(request, 'admin/files.html', {'files': files})

def edit_document(request, id):
    doc = Attachment.objects.get(pk=id)
    form = DocumentForm(instance=doc)
    return render(request, 'documents/form.html', {'form': form})

def tags(request):
    tags = Tag.objects.all()
    return render(request, 'admin/tags.html', {'tags': tags})

def edit_tag(request, tag_id='new'):
    if request.method == 'POST':
        if tag_id != 'new':
            tag = Tag.objects.get(pk=tag_id)
            form = TagForm(request.POST, instance=tag)
        else:
            form = TagForm(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _(u'Tagi tallennettu'))
            return redirect('/admin/tags/')
    else:
        form = TagForm()

    return render(request, 'admin/tag_form.html', {'form': form,
        'tag_id': tag_id})

def settings(request):
    if request.method == 'POST':
        config = dict()
        for k, v in request.POST.items():
            field = Configuration.objects.get_or_create(key=k)[0]
            field.value = v
            field.save()
            config[k] = v

        # must use cache and not session since it's shared among
        # all the users of the system
        cache.set('config', config, 60*60*24*1)
        messages.add_message(request, messages.INFO, _(u'Asetukset tallennettu'))
        return redirect('/admin/settings/')
    
    config = Configuration.conf()
    return render(request, 'admin/settings.html', {'config': config})

def statuses(request):
    statuses = Status.objects.all()
    return render(request, 'admin/statuses.html', {'statuses': statuses})

def status_form(request, status_id=0):
    form = StatusForm()

    if int(status_id) > 0:
        status = Status.objects.get(pk=status_id)
        form = StatusForm(instance=status)

    return render(request, 'admin/status_form.html', {
        'form': form, 'status_id': status_id
        })

def gsx_accounts(request):
    accounts = GsxAccount.objects.all()
    return render(request, 'admin/gsx_accounts.html', {'accounts': accounts})

def gsx_form(request, id=0):
    form = GsxAccountForm()
  
    if int(id) > 0:
        act = GsxAccount.objects.get(pk=id)
        form = GsxAccountForm(instance=act)
        
    return render(request, 'admin/gsx_form.html', {'form': form, 'account_id': id})

def gsx_save(request, account_id):
    cache.delete('gsx_session')

    form = GsxAccountForm(request.POST)

    if int(account_id) > 0:
        act = GsxAccount.objects.get(pk=account_id)
        form = GsxAccountForm(request.POST, instance=act)

    if form.is_valid():
        act = form.save()
        messages.add_message(request, messages.INFO, _(u'GSX tili tallennettu'))
        return redirect('/admin/gsx/accounts/')

    return render(request, 'admin/gsx_form.html', {'form': form,
        'account_id': account_id})

def gsx_remove(request, id=None):
    if 'id' in request.POST:
        act = GsxAccount.objects.get(pk=request.POST.get('id'))
        act.delete()
        messages.add_message(request, messages.INFO, _(u'GSX tili poistettu'))
        redirect('/admin/gsx/accounts/')
    else:
        act = GsxAccount.objects.get(pk=id)
    
    return render(request, 'admin/gsx_remove.html', {'account': act})

def fields(req):
    fields = Property.objects.all()
    return render(req, 'admin/fields/index.html', {'fields' : fields})

def edit_field(request, field_id='new'):
    form = FieldForm()

    if request.method == 'POST':
        if field_id != 'new':
            field = Property.objects.get(pk=field_id)
            form = FieldForm(request.POST, instance=field)
        else:
            form = FieldForm(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _(u'Kenttä tallennettu'))
            return redirect('/admin/fields/')
    else:
        if field_id != 'new':
            field = Property.objects.get(pk=field_id)
            form = FieldForm(instance=field)
    
    return render(request, 'admin/fields/form.html', {'form': form,
        'field_id': field_id})

def remove_field(req, id=None):
    if 'id' in req.POST:
        field = Field(id=ObjectId(req.POST['id']))
        field.delete()
        return HttpResponse("Kenttä poistettu")
    else:
        field = Field.objects(pk=ObjectId(id))[0]
    
    return render(req, 'admin/fields/remove.html', field)

def templates(req):
    templates = Template.objects.all()
    return render(req, 'admin/templates.html', {'templates': templates})

def edit_template(req, template_id=None):
    form = TemplateForm()

    if req.method == 'POST':
        form = TemplateForm(req.POST)
        if 'id' in req.POST:
            template = Template.objects.get(pk=req.POST['id'])
            form = TemplateForm(req.POST, instance=template)

        if form.is_valid():
            form.save()
            messages.add_message(req, messages.INFO, _(u'Pohja tallennettu'))
            return redirect('/admin/templates/')
    else:
        if template_id:
            template = Template.objects.get(pk=template_id)
            form = TemplateForm(instance=template)
    
    return render(req, 'admin/template_form.html', {'form': form})
  
def remove_template(req, id):
    pass

def users(request):
    users = User.objects.all()
    return render(request, 'admin/users.html', {'users': users})

def groups(request):
    groups = Group.objects.all()
    return render(request, 'admin/groups.html', {'groups': groups})

def edit_group(request, id=None):
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _(u'Ryhmä tallennettu'))
            return redirect('/admin/groups/')
    if id:
        group = Group.objects.get(pk=id)
        form = GroupForm(instance=group)

    return render(request, 'admin/group_form.html', {'form': form})

def edit_user(req, id=None):
    user = User()
    locations = Location.objects.all()

    if id:
        user = User.objects.get(pk=id)
        form = UserForm(instance=user)
    else:
        form = UserForm()

    return render(req, 'admin/user_form.html', {
        'user': user, 'locations': locations, 'form': form
        })
  
def locations(req):
    locations = Location.objects.all()
    return render(req, 'admin/locations.html', {'locations': locations})

def edit_location(req, id=None):
    if req.method == 'POST':
        form = LocationForm(req.POST)
        if 'id' in req.POST:
            location = Location.objects.get(pk=req.POST['id'])
            form = LocationForm(req.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.add_message(req, messages.INFO, _(u'Sijainti tallennettu'))
            return redirect('/admin/locations/')
    else:
        if id:
            location = Location.objects.get(pk=id)
            form = LocationForm(instance=location)
        else:
            form = LocationForm()
    
    return render(req, 'admin/location_form.html', {'form': form})
  
def save_user(request):
    if 'id' in request.POST:
        user = User.objects.get(pk=request.POST['id'])
        form = UserForm(request.POST, instance=user)
    else:
        form = UserForm(request.POST)

    if form.is_valid():
        user = form.save()
        messages.add_message(request, messages.INFO, _(u'Käyttäjä tallennettu'))
        return redirect('/admin/users/')
    else:
        return render(request, 'admin/user_form.html', {'form': form})

def save_status(req, status_id):
    if int(status_id) > 0:
        status = Status.objects.get(pk=status_id)
        form = StatusForm(req.POST, instance=status)
    else:
        form = StatusForm(req.POST)

    if form.is_valid():
        form.save()
        messages.add_message(req, messages.INFO, _(u'Status tallennettu'))
        return redirect('/admin/statuses/')

    return render(req, 'admin/status_form.html', {'form': form})

def queues(req):
    queues = Queue.objects.all()
    return render(req, 'admin/queues.html', {'queues': queues})

def edit_queue(request, id=None):
    statuses = Status.objects.all()

    if id:
        queue = Queue.objects.get(pk=id)
        form = QueueForm(instance=queue)
    else:
        form = QueueForm()
        queue = Queue()

    return render(request, 'admin/queue-form.html', {
    	'queue': queue,
    	'form': form,
        'statuses': statuses
    })

def save_queue(request):
    if 'id' in request.POST:
        q = Queue.objects.get(pk=request.POST['id'])
        form = QueueForm(request.POST, request.FILES, instance=q)
    else:
        q = Queue()
        form = QueueForm(request.POST, request.FILES)

    if form.is_valid():
        q = form.save()
    else:
        return render(request, 'admin/queue-form.html', {'form': form})

    d = DotExpandedDict(request.POST)

    if d.get('status'):
        for k, s in d['status'].items():
            if s.get('id'):
                status = Status.objects.get(pk=s['id'])
                QueueStatus.objects.create(status=status, queue=q,
                    limit_green=s['limit_green'],
                    limit_yellow=s['limit_yellow'],
                    limit_factor=s['limit_factor'])
    
    messages.add_message(request, messages.INFO, _(u'Jono tallennettu'))
    return redirect('/admin/queues/')

def remove_queue(req, id=None):
    if 'id' in req.POST:
        queue = Queue.objects.get(pk=req.POST['id'])
        queue.delete()
        return HttpResponse('Jono poistettu')
    else:
        queue = Queue.objects.get(pk=id)
    
    return render(req, 'admin/remove-queue.html', queue)

def product_groups(req):
    groups = ProductGroup.objects.all()
    return render(req, 'admin/products/groups.html', {'groups': groups})

def edit_product_group(req, group_id=0):
    group = ProductGroup()
    
    if int(group_id) > 0:
        group = ProductGroup.objects.get(pk=group_id)
        form = ProductGroupForm(instance=group)
    else:
        form = ProductGroupForm()

    if req.method == 'POST':
        if group:
            form = ProductGroupForm(req.POST, instance=group)
        else:
            form = ProductGroupForm(req.POST)

        if form.is_valid():
            form.save()
            messages.add_message(req, messages.INFO, _(u'Ryhmä tallennettu'))
            return redirect('/admin/products/groups/')

    return render(req, 'admin/products/group_form.html', {
        'form': form,
        'group_id': group_id
        })
