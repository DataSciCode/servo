import json
from django.http import HttpResponse
from django.shortcuts import render
from bson.objectid import ObjectId

from servo3.models import Document

def index(req):
  """docstring for index"""
  files = Document.objects
  return render(req, 'documents/index.html', {'files': files})
  
  
def create(req):
  doc = Document()
  return render(req, 'documents/form.html', {'file': doc})
  
def save(req):
  doc = Document()
  f = req.FILES['incoming']
  doc.name = req.POST.get('name', f.name)
  doc.content = f.read()
  doc.save()
  
  return HttpResponse(json.dumps({'name': doc.name, 'id': str(doc.id)}), content_type="application/json")
  
def view(req, id):
  doc = Document.objects(id = ObjectId(id)).first()
  return HttpResponse(doc.content.read(), content_type="application/pdf")
  
def remove(req, id = None):
  if 'id' in req.POST:
    doc = Document.objects(id = ObjectId(req.POST['id'])).first()
    doc.content.delete()
    doc.delete()
    return HttpResponse('Tiedosto poistettu')
  else:
    doc = Document.objects(id = ObjectId(id)).first()
    return render(req, 'documents/remove.html', doc)
  