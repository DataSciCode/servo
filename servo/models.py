#coding=utf-8
from django.db import models
from datetime import datetime

class Customer(models.Model):
    name = models.CharField(default="Uusi asiakas", max_length=255)
    """path is a comma-separated list of Customer ids with the last one always being the
    current customer
    """
    path = models.TextField()
    #properties = DictField()

    def get_indent(self):
        """docstring for get_indent"""
        return self.path.count(',')+1

    def fullname(self):
        """Get the entire info tree for this customer, upwards
        """
        title = []

        for c in self.path.split(','):
            customer = Customer.objects(id = ObjectId(c))[0]
            title.append(customer.name)

        title.reverse()

        return str(', ').join(title)

    def fullprops(self):
        """Get the combined view of all the properties for this customer
        """
        props = {}
        for c in self.path.split(','):
            parent = Customer.objects(id = ObjectId(c))[0]
            for key, value in parent.properties.items():
                props[key] = value

        return props

    def __unicode__(self):
        return self.name

class Location(models.Model):
    title = models.CharField(default = "Uusi sijainti", max_length=255)
    description = models.TextField()
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    address = models.CharField(max_length=32)
    shipto = models.CharField(max_length=32)
    zip = models.CharField(max_length=8)
    city = models.CharField(max_length=16)

class Attachment(models.Model):
    name = models.CharField(default="Uusi tiedosto", max_length=255)
    content = models.FileField(upload_to="attachments")
    content_type = models.CharField(max_length=64)
    description = models.TextField()
    uploaded_by = models.CharField(default="filipp", max_length=32)
    uploaded_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(default=datetime.now())

    tags = models.TextField()

class Spec(models.Model):
    title = models.CharField(max_length=255)
    #properties = DictField()
    path = models.TextField()

class Article(models.Model):
    title = models.CharField(default = "Uusi artikkeli", max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=32)
    updated_at = models.DateTimeField()
    tags = models.TextField()
    created_at = models.DateTimeField(default = datetime.now())

class Device(models.Model):
    sn = models.CharField(max_length=32)
    description = models.TextField()

    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    purchased_on = models.DateField()
    notes = models.TextField()

    #gsx_data = DictField()
    spec = models.ForeignKey('Spec')

class Product(models.Model):
    #gsx_data = DictField()
    title = models.CharField(default = "Uusi tuote", max_length=255)
    warranty_period = models.IntegerField(default = 0)

    code = models.CharField(default = "", max_length=32)
    shelf = models.CharField(default = "", max_length=8)
    brand = models.CharField(default = "", max_length=32)

    pct_vat = models.DecimalField(decimal_places=2, max_digits=4)
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4)
    price_notax = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_sales = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_purchase = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_exchange = models.DecimalField(default = 0, decimal_places=2, max_digits=6)

    tags = models.TextField(models.CharField(max_length = 30))

    amount_minimum = models.IntegerField(default = 0)
    is_serialized = models.BooleanField(default = False)

    attachments = models.ForeignKey('Attachment')
  
    def tax(self):
        return self.price_sales - self.price_notax

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
  
class Tag(models.Model):
    title = models.CharField(default = 'Uusi tagi', max_length=255)
    type = models.CharField(max_length=32)
  
class Configuration(models.Model):
    company_name = models.CharField(max_length=255)
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4) # the default margin percent for new products
    repair_rate = models.DecimalField(decimal_places=2, max_digits=4)
    pct_vat = models.DecimalField(decimal_places=2, max_digits=4) # default VAT for new products
    encryption_key = models.CharField(max_length=64)

    mail_from = models.EmailField(default = 'servo@example.com')
    imap_host = models.CharField(max_length=255)
    imap_user = models.CharField(max_length=32)
    imap_password = models.CharField(max_length=32)
    imap_ssl = models.BooleanField(default=True)
    smtp_host = models.CharField(max_length=32)

    sms_url = models.CharField(max_length=255)
    sms_user = models.CharField(max_length=32)
    sms_password = models.CharField(max_length=32)
  
class Field(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=32)
    format = models.CharField(max_length=32)
  
class User(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=64)
    fullname = models.CharField(max_length=128, default='Uusi käyttäjä')
    password = models.CharField(max_length=64)
    role = models.CharField(max_length=64)
    location = models.ForeignKey(Location)
  
class OrderItem(models.Model):
    product = models.ForeignKey(Product)
    sn = models.CharField(max_length=32)
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    
class GsxRepair(models.Model):
    #customer_data = DictField()
    symptom = models.TextField()
    diagnosis = models.TextField()

class Template(models.Model):
    title = models.CharField(max_length=64)
    body = models.TextField()
  
class CalendarEvent(models.Model):
    started_at = models.DateTimeField(default = datetime.now())
    finished_at = models.DateTimeField()
    remind_at = models.DateTimeField()
    description = models.CharField(default = "", max_length=255)
    hours = models.IntegerField(default = 8)

class Calendar(models.Model):
    title = models.CharField(default = 'Uusi kalenteri', max_length=128)
    user = models.ForeignKey('User')
    hours = models.IntegerField(default = 0)
    events = models.ForeignKey('CalendarEvent')

class InvoiceItem(Product):
    pass

class PoItem(Product):
    pass

class Invoice(models.Model):
    created_at = models.DateTimeField(default = datetime.now())
    is_paid = models.BooleanField()
    paid_at = models.DateTimeField()
    payment_method = models.CharField(max_length=128)

    customer = models.ForeignKey('Customer')
    customer_info = models.TextField()
    products = models.ForeignKey('InvoiceItem')

    total_tax = models.DecimalField(max_digits=4, decimal_places=2)
    total_margin = models.DecimalField(max_digits=4, decimal_places=2)
    total_payable = models.DecimalField(max_digits=4, decimal_places=2)

class PurchaseOrder(models.Model):
    reference = models.CharField(max_length=32)
    confirmation = models.CharField(max_length=32)
    dispatch_id = models.CharField(max_length=32)
    sales_order = models.CharField(max_length=32)

    date_created = models.DateTimeField(default = datetime.now())
    date_ordered = models.DateTimeField()
    date_arrived = models.DateTimeField()

    carrier = models.CharField(max_length=32)
    supplier = models.CharField(max_length=32)
    tracking_id = models.CharField(max_length=128)
    days_delivered = models.IntegerField()
    products = models.ForeignKey('PoItem')

    def sum(self):
        total = 0
        for p in self.products:
            total += float(p.get('price')*p.get('amount'))

        return total

    def amount(self):
        amount = 0
        for p in self.products:
            amount += p.get('amount')

        return amount
  
class Inventory(models.Model):
    """A slot can refer to basically any model in the system.
    The amount of stocked items is determined by the number of rows
    where slot points to itself.
    Product always points to a Product model.
    The reserved amount of a given item is determined by the number of rows
    with with the order id as slot
    """
    #slot = GenericReferenceField()
    product = models.ForeignKey('Product')
    sn = models.CharField(max_length=32)
    kind = models.CharField(max_length=32) # one of po, order, product, invoice

class GsxAccount(models.Model):
    title = models.CharField(default = "Uusi tili", max_length=128)
    sold_to = models.CharField(max_length=32)
    ship_to = models.CharField(max_length=32)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    environment = models.CharField(max_length=3)
    is_default = models.BooleanField(default=True)

class Property(models.Model):
	key = models.CharField(max_length=32)
	value = models.TextField()

class Status(models.Model):
    FACTORS = (('60', 'Minuuttia'), ('3600', 'Tuntia'), ('86400', 'Päivää'), ('604800', 'Viikkoa'))
    
    title = models.CharField(default = 'Uusi status', max_length=255)
    description = models.TextField()
    limit_green = models.IntegerField()
    limit_yellow = models.IntegerField()
    limit_factor = models.IntegerField()
    
class Queue(models.Model):
    title = models.CharField(default = "Uusi jono", max_length=255)
    description = models.TextField()
    gsx_account = models.ForeignKey(GsxAccount)
    statuses = models.ManyToManyField(Status)
    attachments = models.ForeignKey(Attachment)

class Order(models.Model):
    priority = models.IntegerField(default = 1)
    created_at = models.DateTimeField(default=datetime.now())
    closed_at = models.DateTimeField(null = True)
    followers = models.TextField()
    tags = models.TextField()

    customer = models.ForeignKey(Customer, null=True)
    products = models.ManyToManyField(Product)
    devices = models.ForeignKey(Device, null=True)
    user = models.ForeignKey(User, null=True)
    
    created_by = models.ForeignKey(User, related_name="created_by")

    queue = models.ForeignKey(Queue, null=True)
    status = models.ForeignKey(Status, null=True)

    state = models.CharField(default = "unassigned", max_length=16) # unassigned, open or closed

    status_limit_green = models.IntegerField(null=True)   # timestamp in seconds
    status_limit_yellow = models.IntegerField(null=True)  # timestamp in seconds
    
    #gsx_repairs = models.TextField(DictField())

    def issues(self):
        pass

    def total(self):
        total = 0
        for p in self.products:
            total += p.amount*p.price

        return total

    def can_gsx(self):
        return True

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
        if len(self.devices):
            try:
                return self.devices[0].spec.id
            except AttributeError, e:
                pass
  
    def events(self):
        return Event.objects(ref_order = self)

class Event(models.Model):
    description = models.CharField(max_length=255)
    created_by = models.CharField(default = "filipp", max_length=32)
    created_at = models.DateTimeField(default = datetime.now())
    handled_at = models.DateTimeField(null=True)
    ref_order = models.ForeignKey(Order)
    type = models.CharField(max_length=32)

class Issue(models.Model):
    symptom = models.TextField(default="")
    diagnosis = models.TextField(default="")
    solution = models.TextField(default="")
    
    diagnosed_at = models.DateTimeField()
    diagnosed_by = models.ForeignKey(User, related_name="diagnosed_by")
    
    solved_at = models.DateTimeField()
    solved_by = models.ForeignKey(User, related_name="solved_by")
    
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.CharField(default="filipp", max_length=32)
    order = models.ForeignKey(Order)

class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField(default="")

    smsto = models.CharField(default="", max_length=32)
    mailto = models.EmailField()
    sender = models.CharField(max_length=64)
    recipient = models.CharField(max_length=64)
    created_at = models.DateTimeField(default = datetime.now())
    order = models.ForeignKey(Order)
    attachments = models.ForeignKey(Attachment)

    path = models.TextField() #threading!
    flags = models.TextField()
  
    def indent(self):
        return 1
  
    def send_mail(self):
        import smtplib
        conf = Config.objects.first()
        subject = "Huoltotilaus SRV#%d" %(self.order.number)
        message = "\r\n".join(("From: %s" % conf.mail_from,
          "To: %s" % self.mailto,
          "Subject: %s" % subject,
          "",
          self.body))

        server = smtplib.SMTP(conf.smtp_host)
        server.sendmail(conf.mail_from, self.mailto, message)
        server.quit()
    
    def send_sms(self):
        conf = Config.objects[0]
        import urllib
        params = urllib.urlencode({"username": conf.sms_user,
          "password": conf.sms_password,
          "text" : self.body, "to" : self.smsto})
        f = urllib.urlopen("%s?%s" %(conf.sms_url, params))
        print f.read()
