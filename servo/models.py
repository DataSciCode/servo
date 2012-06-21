#coding=utf-8
from django.db import models
from datetime import datetime

class Tag(models.Model):
    title = models.CharField(default = 'Uusi tagi', max_length=255)
    type = models.CharField(max_length=32)

class Attachment(models.Model):
    name = models.CharField(default = 'Uusi tiedosto', max_length=255)
    
    content_type = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    uploaded_by = models.CharField(default='filipp', max_length=32)
    uploaded_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(default=datetime.now())
    tags = models.ManyToManyField(Tag)
    content = models.FileField(upload_to = 'attachments')

class Configuration(models.Model):
    company_name = models.CharField(max_length=255)
    # the default margin percent for new products
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4, default=0.0)
    # default VAT for new products
    pct_vat = models.DecimalField(decimal_places=2, max_digits=4, default=0.0)
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

class Property(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=32)
    format = models.CharField(max_length=32)

class Customer(models.Model):
    name = models.CharField(default = 'Uusi asiakas', max_length=255)
    """path is a comma-separated list of Customer ids 
    with the last one always being the current customer
    """
    path = models.CharField(max_length=255)

    def property(self, key):
        result = None
        """return the value of a specific property"""
        ci = ContactInfo.objects.filter(customer = self)
        for i in ci:
            if i.key == key:
                result = key.value

        return result

    def properties(self):
        return ContactInfo.objects.filter(customer = self)

    def get_indent(self):
        """docstring for get_indent"""
        return self.path.count(',')+1

    def fullname(self):
        """Get the entire info tree for this customer, upwards
        """
        title = []

        for c in self.path.split(','):
            customer = Customer.objects.get(pk = c)
            title.append(customer.name)

        title.reverse()

        return str(', ').join(title)

    def fullprops(self):
        """Get the combined view of all the properties for this customer
        """
        props = {}
        for c in self.path.split(','):
            parent = Customer.objects.get(pk = c)
            for r in parent.properties():
                props[r.key] = r.value

        return props

    def __unicode__(self):
        return self.name

class ContactInfo(models.Model):
    customer = models.ForeignKey(Customer)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

class Location(models.Model):
    title = models.CharField(default = 'Uusi sijainti', max_length=255)
    description = models.TextField()
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    address = models.CharField(max_length=32)
    shipto = models.CharField(max_length=32)
    zip = models.CharField(max_length=8)
    city = models.CharField(max_length=16)

class Spec(models.Model):
    title = models.CharField(max_length=255, unique=True)
    path = models.TextField()

class SpecInfo(models.Model):
    spec = models.ForeignKey(Spec)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

class Article(models.Model):
    title = models.CharField(default = 'Uusi artikkeli', max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=32)
    updated_at = models.DateTimeField()
    tags = models.TextField()
    created_at = models.DateTimeField(default = datetime.now())
    attachments = models.ManyToManyField(Attachment)

class Device(models.Model):
    sn = models.CharField(max_length=32)
    description = models.TextField()

    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    purchased_on = models.DateField()
    notes = models.TextField()

    gsx_data = models.TextField()
    spec = models.ForeignKey(Spec, null=True)

class Product(models.Model):
    def default_vat():
        conf = Configuration.objects.get(pk = 1)
        return conf.pct_vat

    def default_margin():
        conf = Configuration.objects.get(pk = 1)
        return conf.pct_margin

    #gsx_data = models.TextField(null=True)
    title = models.CharField(default = 'Uusi tuote', max_length=255)
    warranty_period = models.IntegerField(default = 0)

    code = models.CharField(default = '', max_length=32, unique=True)
    shelf = models.CharField(default = '', max_length=8, blank=True)
    brand = models.CharField(default = '', max_length=32, blank=True)
    
    pct_vat = models.DecimalField(decimal_places=2, max_digits=4, default=default_vat)
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4, default=default_margin)
    price_notax = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_sales = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_purchase = models.DecimalField(default = 0, decimal_places=2, max_digits=6)
    price_exchange = models.DecimalField(default = 0, decimal_places=2, max_digits=6)

    amount_minimum = models.IntegerField(default = 0)
    is_serialized = models.BooleanField(default = False)
    
    tags = models.ManyToManyField(Tag, blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)

    def tax(self):
        return self.price_sales - self.price_notax

    def amount_stocked(self, amount = 0):
        """Get or set the stocked amount of this product
        """
        if amount:
            amount = int(amount)
            Inventory.objects.filter(slot = self.id).delete()
            for _ in xrange(amount):
                i = Inventory.objects.create(slot = self.id, product = self)
        try:
            return Inventory.objects.filter(slot = self.id).count()
        except Exception, e:
            return 0

    def amount_ordered(self):
        """Get or set the ordered amount of this product
        """
        try:
            return Inventory.objects.filter(product = self.id, kind = "po").count()
        except Exception, e:
            return 0

    def amount_reserved(self):
        """Get or set the reserved amount of this product
        """
        try:
            return Inventory.objects.filter(product = self.id, kind = "order").count()
        except Exception, e:
            return 0

class User(models.Model):
    email = models.EmailField()
    username = models.CharField(max_length=64)
    fullname = models.CharField(max_length=128, default='Uusi käyttäjä')
    password = models.CharField(max_length=64)
    role = models.CharField(max_length=64)
    location = models.ForeignKey(Location)

    def __unicode__(self):
        return self.fullname

class OrderItem(models.Model):
    product = models.ForeignKey(Product)
    sn = models.CharField(max_length=32)
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=4, decimal_places=2)
    
class GsxRepair(models.Model):
    #customer_data = DictField()
    symptom = models.TextField()
    diagnosis = models.TextField()

class Calendar(models.Model):
    title = models.CharField(default = 'Uusi kalenteri', max_length=128)
    user = models.ForeignKey(User)
    hours = models.IntegerField(default = 0)

    def events(self):
        return CalendarEvent.objects.filter(calendar = self)

class CalendarEvent(models.Model):
    started_at = models.DateTimeField(default = datetime.now())
    finished_at = models.DateTimeField(null=True)
    description = models.CharField(default = '', max_length = 255)
    hours = models.IntegerField(default = 8)
    calendar = models.ForeignKey(Calendar)

class InvoiceItem(Product):
    pass

class PoItem(Product):
    pass

class Invoice(models.Model):
    created_at = models.DateTimeField(default = datetime.now())
    is_paid = models.BooleanField()
    paid_at = models.DateTimeField()
    payment_method = models.CharField(max_length=128)

    customer = models.ForeignKey(Customer)
    customer_info = models.TextField()
    products = models.ForeignKey(InvoiceItem)

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

    products = models.ForeignKey(PoItem)
    carrier = models.CharField(max_length=32)
    supplier = models.CharField(max_length=32)
    tracking_id = models.CharField(max_length=128)
    days_delivered = models.IntegerField()

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
    slot = models.IntegerField()
    product = models.ForeignKey(Product)
    sn = models.CharField(max_length=32)
    kind = models.CharField(max_length=32) # one of po, order, product, invoice

class GsxAccount(models.Model):
    title = models.CharField(default = 'Uusi tili', max_length=128)
    sold_to = models.CharField(max_length=32)
    ship_to = models.CharField(max_length=32)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    environment = models.CharField(max_length=3)
    is_default = models.BooleanField(default=True)

class Status(models.Model):
    FACTORS = (
        ('60', 'Minuuttia'),\
        ('3600', 'Tuntia'),\
        ('86400', 'Päivää'),\
        ('604800', 'Viikkoa')
    )

    title = models.CharField(default = 'Uusi status', max_length=255)

    description = models.TextField()
    limit_green = models.IntegerField(default=0)
    limit_yellow = models.IntegerField(default=0)
    limit_factor = models.IntegerField(default=FACTORS[0])

    def __unicode__(self):
        return self.title

class Queue(models.Model):
    title = models.CharField(default = 'Uusi jono', max_length=255)
    description = models.TextField(blank=True)
    gsx_account = models.ForeignKey(GsxAccount, null=True)
    statuses = models.ManyToManyField(Status, through = 'QueueStatus')
    attachments = models.ManyToManyField(Attachment)

    def __unicode__(self):
        return self.title

class QueueStatus(models.Model):
    limit_green = models.IntegerField()
    limit_yellow = models.IntegerField()
    limit_factor = models.IntegerField()
    queue = models.ForeignKey(Queue)
    status = models.ForeignKey(Status)

class Order(models.Model):
    PRIORITIES = ((0, 'Matala'), (1, 'Normaali'), (2, 'Korkea'))
    priority = models.IntegerField(default = 1, choices=PRIORITIES)
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.ForeignKey(User, related_name = 'created_by')

    closed_at = models.DateTimeField(null = True)
    followed_by = models.ManyToManyField(User, related_name = 'followed_by')

    user = models.ForeignKey(User, null=True)

    tags = models.ManyToManyField(Tag)

    customer = models.ForeignKey(Customer, null=True)
    products = models.ManyToManyField(Product)
    devices = models.ManyToManyField(Device)

    queue = models.ForeignKey(Queue, null=True)
    status = models.ForeignKey(Status, null=True)

    STATES = ((0, 'unassigned'), (1, 'open'), (2, 'closed'))
    state = models.IntegerField(default = 0, max_length=16, choices=STATES)

    status_limit_green = models.IntegerField(null=True)   # timestamp in seconds
    status_limit_yellow = models.IntegerField(null=True)  # timestamp in seconds
    
    attachments = models.ManyToManyField(Attachment)
    #gsx_repairs = models.TextField(DictField())

    def issues(self):
        return Issue.objects.filter(order = self)

    def messages(self):
        return Message.objects.filter(order = self)

    def events(self):
        return Event.objects.filter(order = self)

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
    
    def customer_name(self):
        return 'Filipp Lepalaan'
  
    def customer_id(self):
        return 1
  
    def device_name(self):
        result = ''
        if self.devices.count():
            result = self.devices.all()[0].description

        return result
    
    def customer_name(self):
        if self.customer:
            return self.customer.name
        else:
            return ""
    
    def device_spec(self):
        if self.devices.count():
            return self.devices.all()[0].spec.id

class Event(models.Model):
    description = models.CharField(max_length=255)
    created_by = models.CharField(default = 'filipp', max_length=32)
    created_at = models.DateTimeField(default = datetime.now())
    handled_at = models.DateTimeField(null=True)
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User)
    type = models.CharField(max_length=32)

class Issue(models.Model):
    symptom = models.TextField(default='')
    diagnosis = models.TextField(default='')
    solution = models.TextField(default='')
    
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.CharField(default='filipp', max_length=32)

    order = models.ForeignKey(Order)

class Message(models.Model):
    class Meta:
        ordering = ["id"]

    subject = models.CharField(max_length=255)
    body = models.TextField(default = '')

    mailfrom = models.EmailField(default='', blank=True)
    smsfrom = models.CharField(default='', max_length=32, blank=True)

    mailto = models.EmailField(default='', blank=True)
    smsto = models.CharField(default='', max_length=32, blank=True)
    
    sender = models.ForeignKey(User, related_name='sender')
    recipient = models.ForeignKey(User, null=True, related_name='recipient')
    
    created_at = models.DateTimeField(default = datetime.now())
    order = models.ForeignKey(Order, null=True)

    path = models.CharField(max_length=255) #threading!
    flags = models.CharField(max_length=255, null=True)
    is_template = models.BooleanField(default = False)
    attachments = models.ManyToManyField(Attachment)
    
    def save(self, *args, **kwargs):
        super(Message, self).save(*args, **kwargs)

        if str(self.id) not in self.path.split(','):
            self.path += ',' + str(self.id) # adding a reply to a message

        super(Message, self).save(*args, **kwargs)

    def indent(self):
        return self.path.count(',')+1
  
    def send_mail(self):
        import smtplib
        conf = Configuration.objects.get(pk = 1)
        subject = 'Huoltotilaus SRV#%d' %(self.order.id)
        message = "\r\n".join(("From: %s" % conf.mail_from,
          "To: %s" % self.mailto,
          "Subject: %s" % subject,
          "",
          self.body))

        server = smtplib.SMTP(conf.smtp_host)
        server.sendmail(conf.mail_from, self.mailto, message)
        server.quit()
    
    def send_sms(self):
        import urllib
        conf = Configuration.objects.get(pk = 1)
        params = urllib.urlencode({
            'username': conf.sms_user,
            'password': conf.sms_password,
            'text': self.body,
            'to': self.smsto
        })

        f = urllib.urlopen('%s?%s' %(conf.sms_url, params))
        print f.read()
