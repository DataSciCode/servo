from django.shortcuts import render
from django.http import HttpResponse
from django.utils.datastructures import DotExpandedDict
from django import forms
from servo.models import *

class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue

def index(req):
    queues = Queue.objects.all()
    return render(req, 'queues/index.html', {'queues': queues})

def edit(req, id=None):
    accounts = GsxAccount.objects.all()
    statuses = Status.objects.all()

    if id:
        queue = Queue.objects.get(pk=id)
        form = QueueForm(instance=queue)
    else:
        form = QueueForm()
        queue = Queue()

    return render(req, 'queues/form.html', {
        'queue': queue,
        'form': form,
        'accounts': accounts,
        'statuses': statuses
    })

def save(req):
    if 'id' in req.POST:
        q = Queue.objects.get(pk=req.POST['id'])
    else:
        q = Queue()

    d = DotExpandedDict(req.POST)

    q.title = req.POST.get('title')
    q.description = req.POST.get('description')
    q.gsx_account = GsxAccount.objects.get(pk=req.POST['gsx_account'])

    q.order_template_id = req.POST.get('order_template')
    q.receipt_template_id = req.POST.get('receipt_template')
    q.dispatch_template_id = req.POST.get('dispatch_template', None)

    q.save()

    if d.get('status'):
        for k, s in d['status'].items():
            if s.get('id'):
                status = Status.objects.get(pk=s['id'])
                QueueStatus.objects.create(status=status, queue=q,
                    limit_green=s['limit_green'],
                    limit_yellow=s['limit_yellow'],
                    limit_factor=s['limit_factor'])
    
    return HttpResponse('Jono tallennettu')

def remove(req, id = None):
    if 'id' in req.POST:
        queue = Queue.objects.get(pk = req.POST['id'])
        queue.delete()
        return HttpResponse('Jono poistettu')
    else:
        queue = Queue.objects.get(pk = id)
    
    return render(req, 'queues/remove.html', queue)
