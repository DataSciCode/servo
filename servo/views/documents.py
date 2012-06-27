# coding=utf-8
import json, mimetypes
from django.http import HttpResponse
from django.shortcuts import render
from servo.models import Attachment, Invoice, Configuration
from django import forms

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['content']

def barcode(req, text):
    import barcode
    from barcode.writer import ImageWriter
    code = barcode.get_barcode("Code39", text, writer=ImageWriter())
    # content_type="image/svg+xml"
    return HttpResponse(code.render(None), content_type='image/png')

def index(req):
    files = Attachment.objects.all()
    return render(req, 'documents/index.html', {'files': files})

def edit(req, id):
    doc = Attachment.objects.get(pk=id)
    form = DocumentForm(instance=doc)
    return render(req, 'documents/form.html', {'form': form})

def create(req):
    doc = Attachment()
    form = DocumentForm()
    return render(req, 'documents/form.html', {'form': form})

def save(req):
    mimetypes.init()

    if 'id' in req.POST:
        doc = Attachment.objects.get(pk = req.POST['id'])
    else:
        doc = Attachment()

    f = req.FILES['content']

    type, encoding = mimetypes.guess_type(f.name)
    doc.content = f

    doc.name = req.POST.get('name', f.name)
    doc.content_type = type

    if 'tags' in req.POST:
        doc.tags = req.POST.getlist('tags')
        
    doc.save()
    
    return HttpResponse(json.dumps({'name': doc.name, 'id': doc.id}),
        content_type='application/json')

def view(req, id):
    doc = Attachment.objects.get(pk=id)
    data = doc.content.read()
    return HttpResponse(data, content_type=doc.content_type)
  
def remove(req, id = None):
    if "id" in req.POST:
        doc = Attachment.objects.get(pk = req.POST['id'])
        doc.content.delete()
        doc.delete()
        return HttpResponse('Tiedosto poistettu')
    else:
        doc = Attachment.objects.get(pk = id)
        return render(req, 'documents/remove.html', {'document': doc})

def output(req, ref, ref_id, doc_id):
    import pystache
    conf = Configuration.objects.get(pk = 1)
    doc = Attachment.objects.get(pk = doc_id)
    #data = Invoice.objects(id = ObjectId(ref_id)).first()
    tpl = doc.content.read().decode("utf-8")

    return HttpResponse(pystache.render(tpl, {
        'data': {},
        'config': conf,
        'location': req.session['user'].location
    }))
