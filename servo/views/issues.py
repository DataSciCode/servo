# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse

from servo.models import Issue, Message, Order

def index(req):
  pass
  
def create(req, order_id = None):
    issue = Issue()
    issue.order = Order.objects.get(pk = order_id)
    templates = Message.objects.filter(is_template = True)
    return render(req, 'issues/form.html', {'issue': issue, 'templates': templates})

def edit(req, id):
    issue = Issue.objects.get(pk = id)
    templates = Message.objects.filter(is_template = True)
    return render(req, 'issues/form.html', {'issue': issue, 'templates': templates})
  
def remove(req, id = None):
    if 'id' in req.POST:
        issue = Issue.objects.get(pk = req.POST['id'])
        issue.delete()
        return HttpResponse('Tehtävä poistettu')
    else:
        issue = Issue.objects.get(pk = id)
        return render(req, 'issues/remove.html', {'issue': issue})

def save(req):
    issue = Issue()

    if 'id' in req.POST:
        issue = Issue.objects.get(pk = req.POST['id'])

    if 'order' in req.POST:
        issue.order = Order.objects.get(pk = req.POST['order'])

    issue.symptom = req.POST['symptom']
    issue.diagnosis = req.POST['diagnosis']
    issue.solution = req.POST['solution']

    issue.save()
    
    return HttpResponse('Tehtävä tallennettu')
