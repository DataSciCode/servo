from django.shortcuts import render
from servo.models import Spec

def index(req):
	specs = Spec.objects.all()
	return render(req, 'specs/index.html', {'specs': specs})

def create(req):
	pass

def save(req):
	pass

def remove(req, id = None):
	pass

def edit(req, id):
	pass
