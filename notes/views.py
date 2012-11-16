# coding=utf-8

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from notes.models import Note
from notes.forms import NoteForm
from orders.models import Order
from servo.models import Template, Attachment
from django.views.decorators.http import require_POST

def edit(req, id=0, kind='note', order_id=None, parent=None,
    smsto='', mailto=''):
    
    if smsto or mailto:
        kind = 'message'
        
    note = Note(order_id=order_id, smsto=smsto, mailto=mailto, kind=kind)
    form = NoteForm(initial={'kind': kind, 'smsto': smsto, 'mailto': mailto})

    if int(id) > 0:
        note = Note.objects.get(pk=id)
        form = NoteForm(instance=note)

    if parent:
        parent = Note.objects.get(pk=parent)
        note.parent = parent
        note.order_id = parent.order_id
        form = NoteForm(initial={
            'order_id': parent.order_id,
            'parent': parent.id,
            'kind': parent.kind,
            'report': parent.report
        })

        if parent.mailfrom:
            form.initial['mailto'] = parent.sender
    
    templates = Template.objects.all()

    return render(req, 'notes/form.html', {'note': note,
        'templates': templates, 'form': form})

def remove(request, id=None):
    if request.method == "POST":
        note = Note.objects.get(pk=id)

        if note.order_id:
            url = note.order.get_absolute_url()
        else:
            url = '/home/messages/unread/'

        note.delete()
        messages.add_message(request, messages.INFO, _(u'Merkintä poistettu'))
        return redirect(url)
    else:
        note = Note.objects.get(pk=id)
        return render(request, 'notes/remove.html', {'note': note})

@require_POST
def save(request, kind='note', note_id="new"):
    # note is being saved
    data = request.POST.copy()

    data['created_by'] = request.user.id
    data['recipient'] = request.user.id
    data['sender'] = request.user.email

    # editing an instance
    if 'id' in data:
        note = Note.objects.get(pk=data.get('id'))
        form = NoteForm(data, instance=note)
    else:
        form = NoteForm(data)
    
    if not form.is_valid():
        print form.errors
        return render(request, 'notes/form.html', {'form': form})

    note = form.save()

    if 'content' in request.FILES:
        a = Attachment(uploaded_by=request.user)
        a.from_file(request.FILES['content'])
        note.attachments.add(a)
        note.save()

    msg = _(u'Merkintä tallennettu')

    if 'order' in data:
        messages.add_message(request, messages.INFO, msg)
        return redirect('/orders/%s/' % data['order'])
    else:
        msg = _(u'Viesti lähetetty') if note.mailto else msg
        messages.add_message(request, messages.INFO, msg)
        return redirect('/home/messages/%d/' % note.id)

def template(request, id):
    tpl = Template.objects.get(pk=id)
    return HttpResponse(tpl.content)

def view(req, id):
    pass

def index(req):
    pass
