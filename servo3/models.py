#coding=utf-8

from mongoengine import *
from datetime import datetime
from bson.objectid import ObjectId

connect('servo')

class Device(Document):
  sn = StringField()
  description = StringField(required=True)
  username = StringField()
  password = StringField()
  purchased_on = StringField()
  notes = StringField()
  
  @classmethod
  def to_python(self, blaa):
    """docstring for to_python"""
    return blaa
  
class Product(Document):
  meta = { 'ordering': ['-id'] }
  number = SequenceField()
  
  gsx_data = DictField()
  warranty_period = IntField()
  
  code = StringField(default = "")
  shelf = StringField(default = "")
  brand = StringField(default = "")
  
  pct_vat = DecimalField()
  pct_margin = DecimalField()
  price_notax = DecimalField(default = 0)
  price_sales = DecimalField(default = 0)
  price_purchase = DecimalField(default = 0)
  price_exchange = DecimalField(default = 0)
  
  tags = ListField(StringField(max_length = 30))
  title = StringField(required=True, default = "Uusi tuote")
  
  amount_minimum = IntField(default = 0)
  is_serialized = StringField(max_length = 1, default = "Y")
  
  attachments = ListField(Document)
  
  # Get or set the stocked amount of this product
  def amount_stocked(self, amount = 0):
    if amount:
      amount = int(amount)
      Inventory.objects(slot = self).delete()
      for _ in xrange(amount):
        i = Inventory(slot = self, product = self)
        i.save()
    try:
      return Inventory.objects(slot = self).count()
    except Exception, e:
      return 0
  
  # Get or set the ordered amount of this product
  def amount_ordered(self):
    try:
      return Inventory.objects(product = self, kind = "po").count()
    except Exception, e:
      return 0
  
  # Get or set the reserved amount of this product
  def amount_reserved(self):
    try:
      return Inventory.objects(product = self, kind = "order").count()
    except Exception, e:
      return 0
      
class Attachment(Document):
  name = StringField(default = 'Uusi tiedosto')
  content = FileField()
  description = StringField()
  uploaded_by = StringField(default="filipp")
  uploaded_at = DateTimeField(default=datetime.now())

  @classmethod
  def to_python(self, blaa):
    """docstring for to_python"""
    return blaa
  
class Tag(Document):
  title = StringField(required = True, default = 'Uusi tagi')
  type = StringField(required = True)
  
class Config(Document):
  company_name = StringField()
  pct_margin = DecimalField() # the default margin percent for new products
  repair_rate = DecimalField()
  pct_vat = DecimalField() # default VAT for new products
  encryption_key = StringField()
  
  mail_from = EmailField(default = 'servo@example.com')
  imap_host = StringField()
  imap_user = StringField()
  imap_password = StringField()
  imap_ssl = BooleanField(default=True)
  smtp_host = StringField()
  
  sms_url = StringField()
  sms_user = StringField()
  sms_password = StringField()
  
class Field(Document):
  title = StringField(required=True)
  type = StringField(required=True)
  format = StringField()
  
class Location(Document):
  title = StringField(required=True, default="Uusi sijainti")
  description = StringField()
  phone = StringField()
  email = EmailField()
  address = StringField()
  shipto = StringField()
  
class GsxAccount(Document):
  title = StringField(default="Uusi tili")
  sold_to = StringField()
  ship_to = StringField()
  username = StringField()
  password = StringField()
  environment = StringField()
  is_default = BooleanField(default=True)

class Status(Document):
  title = StringField(default="Uusi status")
  description = StringField()
  limit_green = IntField()
  limit_yellow = IntField()
  limit_factor = IntField()
    
class Queue(Document):
  title = StringField(default = "Uusi jono")
  description = StringField()
  gsx_account = ReferenceField(GsxAccount)
  statuses = DictField()
  attachments = ListField()
  
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
  
class User(Document):
  email = StringField(max_length=128, required=True)
  username = StringField(max_length=64, required=True)
  fullname = StringField(max_length=128, required=True, default='Uusi käyttäjä')
  password = StringField(max_length=64, required=True)
  role = StringField(max_length=64, required=True)
  location = ReferenceField(Location)
  
class OrderItem(EmbeddedDocument):
  product = ReferenceField(Product)
  sn = StringField()
  amount = IntField(required = True)
  price = DecimalField()
  
  @classmethod
  def to_python(self, blaa):
    """docstring for to_python"""
    return blaa
    
class GsxRepair(EmbeddedDocument):
  customer_data = DictField()
  symptom = StringField()
  diagnosis = StringField()
  
class Order(Document):
  number = SequenceField()
  priority = IntField()
  created_at = DateTimeField(default=datetime.now())
  closed_at = DateTimeField()
  followers = ListField()
  customer = ReferenceField(Customer)
  tags = ListField()
  products = ListField(EmbeddedDocumentField(OrderItem))
  devices = ListField(Device)
  user = ReferenceField(User)
  queue = ReferenceField(Queue)
  status = ReferenceField(Status)
  
  status_limit_green = IntField()   # timestamp in seconds
  status_limit_yellow = IntField()  # timestamp in seconds
  
  gsx_repair = DictField()
  
  def can_gsx(self):
    return True
  
  def issues(self):
    return Issue.objects(order = self)
    
  def messages(self):
    return Message.objects(order = self)
    
  def status_name(self):
    if self.status:
      return self.status.title
    else:
      return "Ei statusta"
  
  def status_id(self):
    if self.status:
      return self.status.id
    else:
      return None
  
  def status_img(self):
    from time import time
    if not self.status:
      return 'undefined'
    else:
      if time() < self.status_limit_green:
        return "green"
      if time() < self.status_limit_yellow:
        return "yellow"
      if time() > self.status_limit_yellow:
        return "red"
  
  def device(self):
    return "Ei laitetta"
    
  def customer_name(self):
    return 'Filipp Lepalaan'
  
  def customer_id(self):
    return 1
  
  def device_name(self):
    if not self.devices:
      return ''
    else:
      return self.devices[0]['description']
  
  def customer_name(self):
    if self.customer:
      return self.customer.name
    else:
      return ""
    
  def device_spec(self):
    return 1
  
  def events(self):
    """docstring for events"""
    return Event.objects(ref_order = self)

class Issue(Document):
  symptom = StringField(required=True, default="")
  diagnosis = StringField(default="")
  solution = StringField(default="")
  
  diagnosed_at = DateTimeField()
  diagnosed_by = ReferenceField(User)
  
  solved_at = DateTimeField()
  solved_by = ReferenceField(User)
  
  created_at = DateTimeField(default=datetime.now())
  created_by = StringField(default='filipp')
  
  order = ReferenceField(Order)
  
class Message(Document):
  subject = StringField()
  body = StringField(default='')
  sender = StringField(default='filipp')
  created_at = DateTimeField(default=datetime.now())
  mailto = StringField(default='')
  smsto = StringField(default='')
  order = ReferenceField(Order)
  attachments = ListField(Attachment)
  
  path = StringField() #threading!
  
  def indent(self):
    return 1
    
  def send_mail(self):
    conf = Config.objects[0]
    import smtplib
    server = smtplib.SMTP(conf.smtp_host)
    server.sendmail(conf.mail_from, self.mailto, self.body)
    server.quit()
    
  def send_sms(self):
    conf = Config.objects[0]
    import urllib
    params = urllib.urlencode({'username': conf.sms_user, 'password': conf.sms_password,\
      'text' : self.body, 'to' : self.smsto})
    f = urllib.urlopen("%s?%s" %(conf.sms_url, params))
    print f.read()

class Template(Document):
  title = StringField(required=True)
  body = StringField(required=True)
  
class Calendar(Document):
  title = StringField(required=True)
  username = StringField()
  events = DictField()

class Invoice(Document):
  number = SequenceField()
  created_at = DateTimeField(default=datetime.now())
  paid_at = DateTimeField()
  total = DecimalField()
  items = ListField(OrderItem)
  
class PurchaseOrder(Document):
  number = SequenceField()
  reference = StringField()
  confirmation = StringField()
  dispatch_id = StringField()
  sales_order = StringField()
  
  date_created = StringField()
  date_ordered = StringField()
  date_arrived = StringField

  supplier = StringField()
  days_delivered = StringField()
  carrier = StringField()
  tracking_id = StringField()
  products = ListField(DictField())
  
  def sum(self):
    total = 0
    for p in self.products:
      total += float(p.get('price')*p.get('amount'))
    
    return total
  
  def amount(self):
    amount = 0
    for p in self.products:
      amount += p['amount']
    
    return amount
  
class Event(Document):
  meta = { 'ordering': ['-id'] }
  description = StringField()
  created_by = StringField(default = "filipp")
  created_at = DateTimeField(default = datetime.now())
  handled_at = DateTimeField()
  ref_order = ReferenceField(Order)
  type = StringField()
  
class Calendar(Document):
  title = StringField(required=True)
  user = ReferenceField(User)
  events = ListField(DictField)
  
class Inventory(Document):
  """
  A slot can refer to basically any model in the system.
  The amount of stocked items is determined by the number of rows
  where slot points to itself.
  Product always points to a Product model.
  The reserved amount of a given item is determined by the number of rows
  with with the order id as slot
  """
  slot = GenericReferenceField()
  product = ReferenceField(Product)
  sn = StringField()
  kind = StringField() # one of po, order, product, invoice
  