from mongoengine import *
from datetime import datetime
from pymongo.objectid import ObjectId

connect('servo')

class Field(Document):
  title = StringField(required=True)
  type = StringField(required=True)
  format = StringField()
  
class Location(Document):
  title = StringField(required=True)
  description = StringField()
  phone = StringField()
  email = EmailField()
  address = StringField()
  
class Event(Document):
  description = StringField()
  created_at = DateTimeField(default=datetime.now())
  handled_at = DateTimeField()
  
class GsxAccount(Document):
  title = StringField(default="Uusi tili")
  sold_to = StringField()
  ship_to = StringField()
  username = StringField()
  password = StringField()
  environment = StringField()
  is_default = StringField(max_length=1, default='Y')

class Queue(Document):
  title = StringField(default = "Uusi jono")
  description = StringField()
  gsx_account = ReferenceField(GsxAccount)

class Order(Document):
  number = SequenceField()
  priority = IntField()
  created_at = DateTimeField(default=datetime.now())
  closed_at = DateTimeField()
  
  def messages(self):
    return Message.objects
    
  def status(self):
    return "Ei statusta"
  
  def device(self):
    return "Ei laitetta"
  
  def relative_age(self):
    pass

class User(Document):
  email = StringField(max_length=128, required=True)
  username = StringField(max_length=64, required=True)
  fullname = StringField(max_length=128, required=True)
  password = StringField(max_length=64, required=True)
  role = StringField(max_length=64, required=True)
  location = ReferenceField(Location)

class Issue(Document):
  symptom = StringField(required=True)
  diagnosis = StringField()
  solution = StringField()
  solved_at = DateTimeField()
  solved_by = ReferenceField(User)
  order = ReferenceField(Order)

class Message(Document):
  subject = StringField()
  body = StringField()
  sender = StringField()
  mailto = StringField()
  smsto = StringField()
  order = ReferenceField(Order)

class Status(Document):
  title = StringField(default="Uusi status")
  description = StringField()

class Product(Document):
  number = SequenceField()
  code = StringField()
  title = StringField(required=True)
  brand = StringField()
  tags = ListField(StringField(max_length=30))
  
  price_purchase = DecimalField()
  price_sales = DecimalField()
  price_exchange = DecimalField()
  
  amount_stocked = IntField(default=0)
  amount_ordered = IntField(default=0)
  amount_reserved = IntField(default=0)

class Template(Document):
  title = StringField(required=True)
  body = StringField(required=True)

class Customer(Document):
  meta = { 'ordering': ['path', '-id'] }
  number = SequenceField()
  name = StringField(required=True, default="Uusi asiakas")
  """
  path is a comma-separated list of Customer ids with the last one always being the
  current customer
  """
  path = StringField()
  properties = DictField()
  
  def get_indent(self):
    """docstring for get_indent"""
    return self.path.count(',')+1
  
  def fullname(self):
    """
    Get the entire info tree for this customer, upwards
    """
    title = []
    
    for c in self.path.split(','):
      customer = Customer.objects(id = ObjectId(c))[0]
      title.append(customer.name)
    
    title.reverse()
    
    return str(', ').join(title)

  def fullprops(self):
    """
    Get the combined view of all the properties for this customer
    """
    props = {}
    for c in self.path.split(','):
      parent = Customer.objects(id = ObjectId(c))[0]
      for key, value in parent.properties.items():
        props[key] = value
    
    return props

class Calendar(Document):
  title = StringField(required=True)
  username = StringField()
  events = DictField()

class Invoice(Document):
  number = SequenceField()
  created_at = DateTimeField(default=datetime.now())
  paid_at = DateTimeField()
  items = DictField()
  total = DecimalField()
