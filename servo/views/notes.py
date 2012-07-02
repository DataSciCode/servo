# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from servo.models import Note, Message, Order

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note

def edit(req, id=None, kind=0, order_id=None, parent_id=None):
    if req.method == 'POST':
        note = Note(created_by=req.user,
            order_id=req.POST.get('order_id'))
        note.description = req.POST.get('description')
        note.kind = req.POST.get('kind')
        note.parent_id = req.POST.get('parent_id')
        note.save()
        return HttpResponse('Tehtävä tallennettu')
    else:
        id = ''
        if parent_id:
            parent = Note.objects.get(pk=parent_id)
            note = Note(parent_id=parent_id, order_id=parent.order_id,
                kind=kind)
        else:
            note = Note(order_id=order_id)

        form = NoteForm()
        templates = Message.objects.filter(is_template=True)
        return render(req, 'notes/form.html', {'note': note,
            'templates': templates, 'form': form, 'id': id})

def remove(req, id=None):
    if 'id' in req.POST:
        note = note.objects.get(pk=req.POST['id'])
        note.delete()
        return HttpResponse('Tehtävä poistettu')
    else:
        note = note.objects.get(pk=id)
        return render(req, 'notes/remove.html', {'note': note})

def save(req):
    note = Note()

    if 'id' in req.POST:
        note = Note.objects.get(pk=req.POST['id'])

    if 'order' in req.POST:
        note.order = Order.objects.get(pk=req.POST['order'])

    note.symptom = req.POST['symptom']
    note.diagnosis = req.POST['diagnosis']
    note.solution = req.POST['solution']

    note.save()
    
    return HttpResponse('Tehtävä tallennettu')
