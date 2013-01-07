# coding=utf-8
import logging, hashlib

from datetime import datetime
from django.template import RequestContext
from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse

from django.core.cache import cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.datastructures import DotExpandedDict
from django.utils.datastructures import DotExpandedDict

from django.utils.translation import ugettext as _

from servo.models.common import *
from servo.forms.admin import *
from servo.models.account import UserProfile

def documents(request):
    files = Attachment.objects.all()
    if request.is_ajax():
        return HttpResponse(files.count())

    return render(request, 'admin/files.html', {'files': files})

def edit_document(request, id):
    doc = Attachment.objects.get(pk=id)
    form = DocumentForm(instance=doc)
    return render(request, 'documents/form.html', {'form': form})

def tags(request):
    tags = Tag.objects.all()
    if request.is_ajax():
        return HttpResponse(tags.count())

    return render(request, 'admin/tags/index.html', {'tags': tags})

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

    return render(request, 'admin/tags/form.html', {'form': form,
        'tag_id': tag_id})

def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, _(u'Tarkista asetukset'))
            return render(request, 'admin/settings.html', {'form': form})

        config = form.save()
        print type(config['logo'])
        # must use cache and not session since it's shared among
        # all the users of the system
        cache.set('config', config, 60*60*24*1)
        messages.add_message(request, messages.INFO, _(u'Asetukset tallennettu'))
        return redirect('/admin/settings/')
    
    config = Configuration.conf()
    form = SettingsForm(initial=config)

    return render(request, 'admin/settings.html', {'form': form})

def statuses(request):
    statuses = Status.objects.all()
    if request.is_ajax():
        return HttpResponse(statuses.count())

    return render(request, 'admin/statuses/index.html', {'statuses': statuses})

def save_status(request, status_id):
    if not status_id == 'new':
        status = Status.objects.get(pk=status_id)
        form = StatusForm(request.POST, instance=status)
    else:
        form = StatusForm(request.POST)

    if form.is_valid():
        form.save()
        messages.add_message(request, messages.INFO, _(u'Status tallennettu'))
        return redirect('/admin/statuses/')

    return render(request, 'admin/status_form.html', {'form': form})

def edit_status(request, status_id):
    form = StatusForm()

    if request.method == 'POST':
        return save_status(request, status_id)

    if not status_id == 'new':
        status = Status.objects.get(pk=status_id)
        form = StatusForm(instance=status)

    return render(request, 'admin/statuses/form.html', {
        'form': form, 'status_id': status_id
        })

def gsx_accounts(request):
    accounts = GsxAccount.objects.all()

    if request.is_ajax():
        return HttpResponse(accounts.count())

    return render(request, 'admin/gsx/index.html', {'accounts': accounts})

def gsx_form(request, account_id):
    form = GsxAccountForm()
    
    if request.method == 'POST':
        return gsx_save(request, account_id)

    if account_id != 'new':
        act = GsxAccount.objects.get(pk=account_id)
        form = GsxAccountForm(instance=act)
        
    return render(request, 'admin/gsx/form.html', {'form': form,
        'account_id': account_id})

def gsx_save(request, account_id):
    cache.delete('gsx_session')

    form = GsxAccountForm(request.POST)

    if account_id != 'new':
        act = GsxAccount.objects.get(pk=account_id)
        form = GsxAccountForm(request.POST, instance=act)

    if form.is_valid():
        if form.cleaned_data['is_default']: # only one account can be default
            GsxAccount.objects.all().update(is_default=False)
        act = form.save()
        messages.add_message(request, messages.INFO, _(u'GSX tili tallennettu'))
        return redirect('/admin/gsx/accounts/')

    return render(request, 'admin/gsx/form.html', {
        'form': form,
        'account_id': account_id
        })

def gsx_remove(request, id=None):
    if 'id' in request.POST:
        act = GsxAccount.objects.filter(pk=request.POST.get('id')).delete()
        messages.add_message(request, messages.INFO, _(u'GSX tili poistettu'))
        return redirect('/admin/gsx/accounts/')
    else:
        act = GsxAccount.objects.get(pk=id)
    
    return render(request, 'admin/gsx/remove.html', {'account': act})

def fields(request):
    fields = Property.objects.all()
    if request.is_ajax():
        return HttpResponse(fields.count())

    return render(request, 'admin/fields/index.html', {'fields' : fields})

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

def remove_field(request, id=None):
    if 'id' in request.POST:
        field = Field(id=ObjectId(request.POST['id']))
        field.delete()
        return HttpResponse("Kenttä poistettu")
    else:
        field = Field.objects(pk=ObjectId(id))[0]
    
    return render(request, 'admin/fields/remove.html', field)

def templates(request):
    templates = Template.objects.all()
    if request.is_ajax():
        return HttpResponse(templates.count())

    return render(request, 'admin/templates/index.html', {'templates': templates})

def edit_template(request, template_id=None):
    form = TemplateForm()

    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if 'id' in request.POST:
            template = Template.objects.get(pk=request.POST['id'])
            form = TemplateForm(request.POST, instance=template)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _(u'Pohja tallennettu'))
            return redirect('/admin/templates/')
    else:
        if template_id:
            template = Template.objects.get(pk=template_id)
            form = TemplateForm(instance=template)
    
    return render(request, 'admin/templates/form.html', {'form': form})
  
def remove_template(req, id):
    pass

def users(request):
    users = User.objects.all()
    if request.is_ajax():
        return HttpResponse(users.count())

    return render(request, 'admin/users/index.html', {'users': users})

def groups(request):
    groups = Group.objects.all()
    if request.is_ajax():
        return HttpResponse(groups.count())

    return render(request, 'admin/users/groups.html', {'groups': groups})

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

    return render(request, 'admin/users/group_form.html', {'form': form})

def remove_user(request, user_id):
    if request.method == "POST":
        User.objects.filter(pk=user_id).delete()
        messages.add_message(request, messages.INFO, _(u'Käyttäjä poistettu'))
        return redirect('/admin/users/')

    user = User.objects.get(pk=user_id)
    return render(request, "admin/users/remove.html", {'user': user})

def edit_user(request, user_id='new'):
    if request.method == "POST":
        return save_user(request, user_id)

    user = User()
    locations = Location.objects.all()

    if user_id == "new":
        form = UserForm()
    else:
        user = User.objects.get(pk=user_id)
        form = UserForm(instance=user)

    return render(request, "admin/users/form.html", {
        'form': form,
        'user': user,
        'user_id': user_id,
        'locations': locations
        })

def save_user(request, user_id):
    if user_id != "new":
        user = User.objects.get(pk=user_id)
        form = UserForm(request.POST, instance=user)
    else:
        form = UserForm(request.POST)

    if form.is_valid():
        user = form.save()
        user.set_password(request.POST['password'])
        user.save()
        messages.add_message(request, messages.INFO, _(u'Käyttäjä tallennettu'))
        return redirect("/admin/users/")
    else:
        return render(request, "admin/users/form.html", {'form': form})

def locations(request):
    locations = Location.objects.all()
    if request.is_ajax():
        return HttpResponse(locations.count())
    return render(request, "admin/locations/index.html", {'locations': locations})

def edit_location(request, id=0):
    if request.method == 'POST':
        form = LocationForm(request.POST)

        if int(id) > 0:
            location = Location.objects.get(pk=id)
            form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 
                _(u"Sijainti tallennettu"))
            return redirect('/admin/locations/')

    if id:
        location = Location.objects.get(pk=id)
        form = LocationForm(instance=location)
    else:
        location = Location()
        form = LocationForm()
    
    form.pk = id
    return render(request, 'admin/locations/form.html', {'form': form})

def queues(request):
    queues = Queue.objects.all()

    if request.is_ajax():
        return HttpResponse(queues.count())

    return render(request, 'admin/queues/index.html', {'queues': queues})

def edit_queue(request, queue_id=None):

    template = 'admin/queues/form.html'

    if queue_id:
        queue = Queue.objects.get(pk=queue_id)
        queue_form = QueueForm(instance=queue, prefix='queue')
    else:
        queue = Queue()
        queue_form = QueueForm(prefix='queue')

    if request.method == 'POST':

        if queue_id is None:
            queue_form = QueueForm(request.POST, request.FILES, prefix='queue')
        else:
            queue = Queue.objects.get(pk=queue_id)
            queue_form = QueueForm(request.POST, request.FILES, instance=queue, prefix='queue')

        if not queue_form.is_valid():
            return render(request, template, {'queue_form': queue_form})

        queue_form.save()

        # process queue's statuses
        queue.queuestatus_set.all().delete()
        data = DotExpandedDict(request.POST)

        if data.get('status'):
            for s in data['status'].values():
                if s.get('status_id'): # status is selected...
                    qs = s
                    qs['queue'] = queue
                    QueueStatus.objects.create(**qs)

        messages.add_message(request, messages.INFO, _(u'Jono tallennettu'))
        return redirect('/admin/queues/')

    selected = list()

    for s in queue.queuestatus_set.all():
        selected.append(s.status.pk)

    statuses = list()

    for s in Status.objects.all():
        if s.id in selected:
            stat = queue.queuestatus_set.get(status_id=s.id)
            s.limit_green = stat.limit_green
            s.limit_yellow = stat.limit_yellow
            s.limit_factor = stat.limit_factor

        statuses.append(s)

    return render(request, template, {
        'queue_form': queue_form,
        'statuses': statuses,
        'selected': selected
    })

def remove_queue(request, id=None):

    queue = Queue.objects.get(pk=id)

    if request.method == 'POST':
        queue.delete()
        messages.add_message(request, messages.INFO, _(u'Jono poistettu'))
        return redirect('/admin/queues/')
        
    return render(request, 'admin/queues/remove.html', {'queue': queue})

def notifications(request):
    return render(request, 'admin/notifications/index.html')

def edit_notification(request, nid):
    return render(request, 'admin/notifications/form.html')
    