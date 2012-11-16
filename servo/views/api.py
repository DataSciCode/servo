import json
from servo.models import *
from django.contrib import auth
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def ok(message):
	msg = json.dumps(dict(ok=message))
	return HttpResponse(msg, content_type='application/json')

def error(message):
	msg = json.dumps(dict(error=message))
	return HttpResponse(msg, content_type='application/json')

@csrf_exempt
@login_required
def orders(request):
	if request.method == 'POST':
		print 'Create a new order'

		data = json.loads(request.body)
		customer = data['customer']
		name = customer.pop('name')
		k, v = customer.items()[0]

		try:
			c = Customer.objects.get(contactinfo__key=k, contactinfo__value=v)
			# found existing customer - update contact info
			for k, v in customer.item():
				ci = ContactInfo.objects.get(key=k, customer=c)
				ci.value = v
				ci.save()
		except Customer.DoesNotExist:
			c = Customer.objects.create(name=name)
			for k, v in customer.items():
				ContactInfo.objects.create(key=k, value=v, customer=c)

		device = data['device']
		d, created = Device.objects.get_or_create(sn=device['sn'], description=device['description'])
		order = Order.objects.create(created_by=request.user, customer=c)
		order.devices.add(d)
		order.save()

		note = Note(body=data['problem'], order=order, created_by=request.user, path='.')
		note.save()

	if request.method == 'PUT':
		print 'Update an order'

	return ok(order.id)

def customers(request):
	pass

def devices(request):
	pass

@login_required
def notes(request, id=None):
	if request.method == 'GET':
		notes = Note.objects.all()
		return HttpResponse(json.dumps(notes), content_type='application/json')
	if request.method == 'POST':
		print 'Create a new note'
		data = json.loads(request.body)
		note = Note()
		note.body = data['body']
		note.save()
		#data = json.loads(request.POST.get('r'))
		return HttpResponse('OK')

@csrf_exempt
def login(request):
	if request.method != 'POST':
		return HttpResponse('Cannot authenticate')
	
	data = json.loads(request.body)

	try:
		user = auth.authenticate(username=data['username'], password=data['password'])
	except Exception, e:
		print e
		return HttpResponse('Invalid credentials for authentication')
	
	try:
		if user.is_active:
			auth.login(request, user)
			return HttpResponse('OK')
	except AttributeError, e:
		return HttpResponse('Authentication failed')
