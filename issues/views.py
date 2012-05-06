# coding=utf-8
from bson.objectid import ObjectId
from django.shortcuts import render
from django.http import HttpResponse

from servo3.models import Issue, Template, Order

def index(req):
  pass
  
def create(req, order_id=None):
  issue = Issue()
  issue.order = order_id
  templates = Template.objects
  return render(req, 'issues/form.html', {'issue': issue, 'templates': templates})
  
def edit(req, id):
  issue = Issue.objects(id=ObjectId(id))[0]
  templates = Template.objects
  return render(req, 'issues/form.html', {'issue': issue, 'templates': templates})
  
def remove(req, id=None):
  if 'id' in req.POST:
    issue = Issue.objects(id=ObjectId(req.POST['id']))
    issue.delete()
    return HttpResponse('Tehtävä poistettu')
  else:
    issue = Issue.objects(id=ObjectId(id))[0]
    return render(req, 'issues/remove.html', issue)
  
def save(req):
  issue = Issue()
  
  if 'id' in req.POST:
    issue = Issue.objects(id=ObjectId(req.POST['id']))[0]
  if 'order' in req.POST:
    issue.order = Order.objects(id=ObjectId(req.POST['order']))[0]
  
  issue.symptom = req.POST['symptom']
  issue.diagnosis = req.POST['diagnosis']
  issue.solution = req.POST['solution']
  
  issue.save()
  
  return HttpResponse('Tehtävä tallennettu')
  