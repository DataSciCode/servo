from django.http import HttpResponse
from django.shortcuts import render

from servo3.models import Document

def index(req):
  """docstring for index"""
  files = Document.objects
  return render(req, 'documents/index.html', {'files': files})
  