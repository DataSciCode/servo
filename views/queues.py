from django.shortcuts import render
from django.http import HttpResponse

from bson.objectid import ObjectId
from servo3.models import *

def index(req):

  queues = Queue.objects
  return render(req, 'queues/index.html', {'queues': queues})

def edit(req, id=None):

  accounts = GsxAccount.objects
  queue = Queue()
  statuses = Status.objects
  if id:
    queue = Queue.objects(id = ObjectId(id))[0]
  
  return render(req, 'queues/form.html', {'queue': queue,
    'accounts': accounts,
    'statuses': statuses})

def save(req):

  q = Queue()
  
  if 'id' in req.POST:
    q = Queue.objects(id = ObjectId(req.POST['id'])).first()
  
  q.title = req.POST['title']
  q.description = req.POST['description']
  q.gsx_account = GsxAccount.objects(id = ObjectId(req.POST['gsx_account'])).first()
  
  for a in req.POST.getlist("attachments"):
    q.attachments.append(Attachment.objects.with_id(ObjectId(a)))

  q.save()
  
  return HttpResponse("Jono tallennettu")
  
def remove(req, id=None):

  if 'id' in req.POST:
    queue = Queue.objects(id = ObjectId(req.POST['id']))
    queue.delete()
    return HttpResponse('Jono poistettu')
  else:
    queue = Queue.objects(id = ObjectId(id)).first()
    return render(req, 'queues/remove.html', queue)
  