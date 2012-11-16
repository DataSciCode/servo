# coding=utf-8
import json, mimetypes
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages

from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from django.utils.translation import ugettext as _

from servo.models import Attachment, Configuration
from orders.models import Invoice

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Attachment

class MyBarcodeDrawing(Drawing):
    def __init__(self, text_value, *args, **kw):
        barcode = createBarcodeDrawing('Code128', value=text_value,
            barHeight=10*mm, humanReadable=True)
        Drawing.__init__(self, barcode.width, barcode.height, *args, **kw)       
        self.add(barcode, name='barcode')

def barcode(req, text):
    d = MyBarcodeDrawing(text)
    binaryStuff = d.asString('png')
    return HttpResponse(binaryStuff, 'image/png')

def create(req):
    doc = Attachment()
    form = DocumentForm()
    return render(req, 'documents/form.html', {'form': form})

def edit(req):
    pass

def save(req):
    mimetypes.init()

    if 'id' in req.POST:
        doc = Attachment.objects.get(pk=req.POST['id'])
    else:
        doc = Attachment()

    f = req.FILES['content']

    type, encoding = mimetypes.guess_type(f.name)
    doc.content = f

    doc.name = req.POST.get('name', f.name)
    doc.content_type = type
    doc.is_template = req.POST.get('is_template', False)

    if 'tags' in req.POST:
        doc.tags = req.POST.getlist('tags')
        
    doc.save()
    
    messages.add_message(req, messages.INFO, _('Tiedosto tallennettu'))
    return redirect('/admin/files/')

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
