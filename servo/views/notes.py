# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from servo.models import Note, Message, Order

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note

def edit(req, id=None, kind=0, order_id=None):
    if req.method == 'POST':
        form = NoteForm(req.POST)
        print form.errors
        form.save()
        return HttpResponse('Tehtävä tallennettu')
    else:
        form = NoteForm({'order': order_id})
        templates = Message.objects.filter(is_template=True)
        return render(req, 'notes/form.html', {'form': form,
            'templates': templates,
            'kind': kind})
  
def remove(req, id=None):
    if 'id' in req.POST:
        note = note.objects.get(pk=req.POST['id'])
        note.delete()
        return HttpResponse('Tehtävä poistettu')
    else:
        note = note.objects.get(pk=id)
        return render(req, 'notes/remove.html', {'note': note})

def save(req):
    note = note()

    if 'id' in req.POST:
        note = note.objects.get(pk=req.POST['id'])

    if 'order' in req.POST:
        note.order = Order.objects.get(pk=req.POST['order'])

    note.symptom = req.POST['symptom']
    note.diagnosis = req.POST['diagnosis']
    note.solution = req.POST['solution']

    note.save()
    
    return HttpResponse('Tehtävä tallennettu')
