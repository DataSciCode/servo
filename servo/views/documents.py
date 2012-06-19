# coding=utf-8

import json, mimetypes

from django.http import HttpResponse
from django.shortcuts import render
from servo.models import Attachment, Invoice, Configuration

def barcode(req, text):
    import barcode
    code = barcode.get_barcode("Code39", text)
    return HttpResponse(code.render(None), content_type="image/svg+xml")

def index(req):
    files = Attachment.objects.all()
    return render(req, "documents/index.html", {"files": files})

def edit(req, id):
    doc = Attachment.objects(id = ObjectId(id)).first()
    return render(req, "documents/form.html", {"file": doc})

def create(req):
    doc = Attachment()
    return render(req, "documents/form.html", {"file": doc})
  
def save(req):
    mimetypes.init()

    if "id" in req.POST:
        doc = Attachment.objects(id = ObjectId(req.POST['id'])).first()
    else:
        doc = Attachment()

    f = req.FILES['incoming']

    type, encoding = mimetypes.guess_type(f.name)

    if "id" in req.POST:
        doc.content.replace(f.read(), content_type=type)
    else:
        doc.content.put(f.read(), content_type=type)

    doc.name = req.POST.get("name", f.name)
    doc.content_type = type

    if "tags" in req.POST:
        doc.tags = req.POST.getlist("tags")
        
    doc.save()
  
    return HttpResponse(json.dumps({"name": doc.name, "id": str(doc.id)}),
        content_type = 'application/json')

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

def output(req, id, ref, ref_id):
    import pystache

    conf = Configuration.objects().first()
    doc = Attachment.objects(id = ObjectId(id)).first()
    data = Invoice.objects(id = ObjectId(ref_id)).first()
    tpl = doc.content.read().decode("utf-8")

    return HttpResponse(pystache.render(tpl, {
        "data": data,
        "config": conf,
        "location": req.session['user'].location
    }))
