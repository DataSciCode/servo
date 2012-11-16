from django.shortcuts import render
from django.http import HttpResponse

from servo.models import Article, Tag

def index(req):
	articles = Article.objects.all()
	return render(req, 'articles/index.html', {'data': articles})

def remove(req, id):
	pass

def edit(req, id):
	pass

def save(req):
	pass

def view(req, id):
	pass
