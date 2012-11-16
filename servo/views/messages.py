from django.shortcuts import render
from django.http import HttpResponse
from django.forms import ModelForm

from servo.models import Message, Order, Attachment, Template

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']

def edit(req, id=None):
    m = Message.objects.get(pk=id)
    templates = Message.objects.filter(is_template=True)
    return render(req, 'messages/form.html', {'message': m,
        'templates': templates})

def save(req):
    m = Message(sender=req.user)

    m.body = req.POST.get('body')
    m.smsto = req.POST.get('smsto', '')
    m.subject = req.POST.get('body', '')
    m.mailto = req.POST.get('mailto', '')
    
    if 'order' in req.session:
        m.order = req.session['order']
        m.recipient = req.session['order'].user

    return HttpResponse('Viesti tallennettu')

