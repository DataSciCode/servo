import json, mimetypes
from django.http import HttpResponse
from django.shortcuts import render
from bson.objectid import ObjectId

from servo3.models import Attachment

def index(req):
  files = Attachment.objects
  return render(req, "documents/index.html", {"files": files})
  
def create(req):
  doc = Attachment()
  return render(req, "documents/form.html", {"file": doc})
  
def save(req):
  mimetypes.init()
  doc = Attachment()
  f = req.FILES['incoming']

  doc.content = f.read()
  doc.name = req.POST.get("name", f.name)
  type, encoding = mimetypes.guess_type(f.name)
  doc.content.content_type = type
  doc.content_type = type

  if "tags" in req.POST:
    doc.tags = req.POST.getlist("tags")

  doc.save()
  
  return HttpResponse(json.dumps({"name": doc.name, "id": str(doc.id)}),
    content_type="application/json")
  
def view(req, id):
  doc = Attachment.objects(id = ObjectId(id)).first()
  data = doc.content.read()
  return HttpResponse(data, content_type=doc.content_type)
  
def remove(req, id = None):
  if "id" in req.POST:
    doc = Attachment.objects(id = ObjectId(req.POST['id'])).first()
    doc.content.delete()
    doc.delete()
    return HttpResponse("Tiedosto poistettu")
  else:
    doc = Attachment.objects(id = ObjectId(id)).first()
    return render(req, "documents/remove.html", doc)
  