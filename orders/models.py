from django.db import models

# Create your models here.
class Order(models.Model):
  """docstring for Order"""
  def __init__(self, arg):
    super(Order, self).__init__()
    self.arg = arg
    