import json, re
from servo3.models import Tag
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def create(req, type):
  tag = Tag(type = type)
  return render(req, 'tags/create.html', tag)
  
def index(req, type):
  results = []
  tags = Tag.objects(type=type).all()
  
  if 'term' in req.GET:
    rex = re.compile("^%s" %req.GET['term'], re.IGNORECASE)
    tags = Tag.objects(type = type, title = rex).all()
  
  for t in tags:
    results.append(t.title)
    
  return HttpResponse(json.dumps(results), content_type="application/json")

@csrf_exempt
def save(req, type):
  t = Tag.objects(title = req.POST['tag'], type = type).first()
  
  if not t:
    t = Tag(type = type, title = req.POST['tag'])
    t.save()
  
  return HttpResponse("OK")
  