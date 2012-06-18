from django.shortcuts import render
from django.http import HttpResponse
from servo.models import Message, Template, Order, Attachment

def index(req):
  messages = Message.objects(recipient = req.session['user'].username).all()
  return render(req, "messages/index.html", {"messages": messages})

def form(req, replyto = None, smsto = None, mailto = None):
  m = Message()
  if smsto:
    m.smsto = smsto
  if mailto:
    m.mailto = mailto

  templates = Template.objects.all()
  return render(req, "messages/form.html", {"message": m, "templates": templates})

def edit(req, id = None):
  m = Message.objects(id = ObjectId(id)).first()
  return render(req, "messages/form.html", {
    "message": m,
    "templates": Template.objects.all()
  })
  
def reply(req, id):
  parent = Message.objects(id = ObjectId(id)).first()
  m = Message(path = parent.path)

  return render(req, "messages/form.html", {
    "message": m,
    "templates": Template.objects.all()
  })
  
def save(req):
  m = Message(sender = req.session.get("user").username)

  m.body = req.POST.get("body")
  m.smsto = req.POST.get("smsto")
  m.subject = req.POST.get("body")
  m.mailto = req.POST.get("mailto")
  
  for a in req.POST.getlist("attachments"):
    doc = Attachment.objects(id = ObjectId(a)).first()
    m.attachments.append(doc)
  
  if "order" in req.session:
    m.order = req.session['order']
  
  if(m.mailto):
    m.send_mail()
  
  if(m.smsto):
    m.send_sms()
  
  m.save()
  
  return HttpResponse("Viesti tallennettu")

def remove(req, id = None):
  if "id" in req.POST:
    msg = Message.objects(id = ObjectId(req.POST['id']))
    msg.delete()
    return HttpResponse("Viesti poistettu")
  else:
    msg = Message.objects(id = ObjectId(id))[0]
    return render(req, "messages/remove.html", msg)
    
def view(req, id):
  m = Message.objects(id = ObjectId(id))[0]
  return render(req, "messages/view.html", m)
  