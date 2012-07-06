import json, re
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from servo.models import Tag

def create(req, kind):
    tag = Tag(kind=kind)
    return render(req, 'tags/create.html', {'tag': tag})
    
def index(req, kind):
    results = []
    tags = Tag.objects.filter(kind=kind).all()
    
    if 'term' in req.GET:
        tags = tags.filter(title__istartswith = req.GET.get('term'))
    
    for t in tags:
        results.append(t.title)
    
    return HttpResponse(json.dumps(results), content_type='application/json')

@csrf_exempt
def save(req, kind):
    try:
        t = Tag.objects.get(title=req.POST['tag'], kind=kind)
    except Exception, e:
        t = Tag(kind=kind, title=req.POST['tag'])
    
    t.times_used += 1
    t.save()
    
    return HttpResponse("OK")
  