import json, re
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from servo.models import Tag

def create(req, type):
    tag = Tag(type=type)
    return render(req, 'tags/create.html', {'tag': tag})
    
def index(req, type):
    results = []
    tags = Tag.objects.filter(type=type).all()
    
    if 'term' in req.GET:
        tags = tags.filter(title__istartswith = req.GET.get('term'))
    
    for t in tags:
        results.append(t.title)
    
    return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_exempt
def save(req, type):
    try:
        t = Tag.objects.get(title=req.POST['tag'], type=type)
    except Exception, e:
        t = Tag(type=type, title=req.POST['tag'])
        t.save()
  
    return HttpResponse("OK")
  