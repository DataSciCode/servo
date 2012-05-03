from django.db import models
from pymongo import Connection

connection = Connection()
db = connection.servo

class Order():
  def all(self):
    collection = db.orders
    return collection.find()
