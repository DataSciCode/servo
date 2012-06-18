from django.shortcuts import render
from django.http import HttpResponse
from servo.models import *

def index(req):
    queues = Queue.objects.all()
    return render(req, "queues/index.html", {"queues": queues})

def edit(req, id = None):
    queue = Queue()
    accounts = GsxAccount.objects.all()
    statuses = Status.objects.all()

    if id:
        queue = Queue.objects.get(pk = id)
    
    return render(req, "queues/form.html", {
        "queue": queue,
        "accounts": accounts,
        "statuses": statuses
    })

def save(req):
    q = Queue()
  
    if 'id' in req.POST:
        q = Queue.objects.get(pk = req.POST['id'])
    
    q.title = req.POST['title']
    q.description = req.POST['description']
    q.gsx_account = GsxAccount.objects.get(pk = req.POST['gsx_account'])

    for a in req.POST.getlist("attachments"):
        q.attachments.append(Attachment.objects.with_id(ObjectId(a)))

    q.save()
    
    return HttpResponse("Jono tallennettu")

def remove(req, id = None):
    if 'id' in req.POST:
        queue = Queue.objects.get(pk = req.POST['id'])
        queue.delete()
        return HttpResponse('Jono poistettu')
    else:
        queue = Queue.objects.get(pk = id)
    
    return render(req, 'queues/remove.html', queue)
