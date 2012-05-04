from django.shortcuts import render
from servo3.models import Product

def create(req, order_id=None):
  p = Product()
  return render(req, 'form.html', p)
