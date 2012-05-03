from django.template import RequestContext
from django.shortcuts import get_object_or_404, render

from pymongo import Connection

connection = Connection()
db = connection.servo

def index(req):
  orders = db.orders.find()
  return render(req, 'index.html', {"data" : orders })
