import json
from servo3.models import Tag
from django.shortcuts import render
from django.http import HttpResponse

def create(req, type):
  tag = Tag(type = type)
  return render(req, 'tags/create.html', tag)
  
def index(req, type=None):
  tags = Tag.objects(type=type)
  return HttpResponse(json.dumps(dict(tags)), content_type="application/json")
  