# coding=utf-8

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from servo.models.note import Note
from servo.forms.note import NoteForm
from servo.models.order import Order
from servo.models.common import Template, Attachment

def edit(request, note_id='new', kind='note', order_id=None, parent=None,
    recipient=''):
    
    if request.method == 'POST':
        return save(request, kind, note_id)
        
    note = Note(order_id=order_id, kind=kind, recipient=recipient)

    if order_id:
        order = Order.objects.get(pk=order_id)
        if order.user is not request.user:
            recipient = order.user

    form = NoteForm(instance=note)

    if note_id != 'new':
        note = Note.objects.get(pk=note_id)
        form = NoteForm(instance=note)

    if parent:
        parent = Note.objects.get(pk=parent)
        note.parent = parent
        note.order_id = parent.order_id
        form = NoteForm(initial={
            'order_id': parent.order_id,
            'parent': parent.id,
            'kind': parent.kind,
            'should_report': parent.should_report
        })

        if parent.sent_at:
            form.initial['recipient'] = parent.sender
    
    templates = Template.objects.all()

    return render(request, 'notes/form.html', {'note': note,
        'templates': templates, 'form': form})

def remove(request, id=None):
    if request.method == 'POST':
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

def save(request, kind='note', note_id='new'):
    # note is being saved
    data = request.POST.copy()

    data['created_by'] = request.user.id
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

    try:
        note = form.save()
    except Exception, e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, 'notes/form.html', {'form': form})

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
        return redirect('/accounts/messages/%d/' % note.id)

def templates(request, template_id=None):
    if template_id:
        tpl = Template.objects.get(pk=template_id)
        return HttpResponse(tpl.content)

    templates = Template.objects.all()
    return render(request, 'notes/templates.html', {'templates': templates})

def view(req, id):
    pass

def index(req):
    pass
