#coding=utf-8
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Tag(models.Model):
    TYPES = ((0, 'Sijainti'))
    title = models.CharField(default='Uusi tagi', max_length=255)
    kind = models.CharField(max_length=32)
    times_used = models.IntegerField()

class Attachment(models.Model):
    name = models.CharField(default='Uusi tiedosto', max_length=255)
    content_type = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    uploaded_by = models.CharField(default='filipp', max_length=32)
    uploaded_at = models.DateTimeField(default=datetime.now())
    updated_at = models.DateTimeField(default=datetime.now())
    tags = models.ManyToManyField(Tag)
    content = models.FileField(upload_to='attachments')
    is_template = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class Configuration(models.Model):
    company_name = models.CharField(max_length=255)
    # the default margin percent for new products
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4,
        default=0.0)
    # default VAT for new products
    pct_vat = models.DecimalField(decimal_places=2, max_digits=4, default=0.0)
    encryption_key = models.CharField(max_length=64)

    mail_from = models.EmailField(default='servo@example.com')
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

    def __unicode__(self):
        return self.title

class Customer(models.Model):
    name = models.CharField(default='Uusi asiakas', max_length=255)
    """path is a comma-separated list of Customer ids 
    with the last one always being the current customer
    """
    path = models.CharField(max_length=255)

    def get_property(self, key):
        result = None
        """return the value of a specific property"""
        ci = ContactInfo.objects.filter(customer=self)
        for i in ci:
            if i.key == key:
                result = i.value

        return result

    # @todo: make these localizable
    def email(self):
        return self.get_property(u'Sähköposti')

    def phone(self):
        return self.get_property(u'Puhelin')

    def properties(self):
        return ContactInfo.objects.filter(customer=self)

    def get_indent(self):
        """docstring for get_indent"""
        return self.path.count(',')+1

    def fullname(self):
        """Get the entire info tree for this customer, upwards
        """
        title = []

        for c in self.path.split(','):
            customer = Customer.objects.get(pk=c)
            title.append(customer.name)

        title.reverse()

        return str(', ').join(title)

    def fullprops(self):
        """Get the combined view of all the properties for this customer
        """
        props = {}
        for c in self.path.split(','):
            parent = Customer.objects.get(pk=c)
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

    def __unicode__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(default = 'Uusi artikkeli', max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=32)
    updated_at = models.DateTimeField()
    tags = models.TextField()
    created_at = models.DateTimeField(default = datetime.now())
    attachments = models.ManyToManyField(Attachment)

class Spec(models.Model):
    title = models.CharField(max_length=255, unique=True)
    path = models.TextField()

class SpecInfo(models.Model):
    spec = models.ForeignKey(Spec)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

class Device(models.Model):
    sn = models.CharField(max_length=32, unique=True, blank=True)
    description = models.CharField(max_length=128)
    username = models.CharField(max_length=32, blank=True)
    password = models.CharField(max_length=32, blank=True)
    purchased_on = models.DateField(blank=True)
    notes = models.TextField(blank=True)
    spec = models.ForeignKey(Spec, null=True)

class Product(models.Model):
    class Meta:
        ordering = ['-id']
        verbose_name = u'Tuote'

    def default_vat():
        conf = Configuration.objects.get(pk=1)
        return conf.pct_vat

    def default_margin():
        conf = Configuration.objects.get(pk=1)
        return conf.pct_margin

    title = models.CharField(default = 'Uusi tuote', max_length=255)
    description = models.TextField(blank=True)
    warranty_period = models.IntegerField(default = 0)

    code = models.CharField(default = '', max_length=32, unique=True, verbose_name = u'koodi')
    shelf = models.CharField(default = '', max_length=8, blank=True)
    brand = models.CharField(default = '', max_length=32, blank=True)

    pct_vat = models.DecimalField(decimal_places=2, max_digits=4, 
        default=default_vat)
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4, 
        default=default_margin)
    price_notax = models.DecimalField(default = 0, decimal_places=2, 
        max_digits=6)
    price_sales = models.DecimalField(default = 0, decimal_places=2, 
        max_digits=6)
    price_purchase = models.DecimalField(default = 0, decimal_places=2, 
        max_digits=6)
    price_exchange = models.DecimalField(default = 0, decimal_places=2, 
        max_digits=6)

    amount_minimum = models.IntegerField(default = 0)
    is_serialized = models.BooleanField(default = False)
    
    tags = models.ManyToManyField(Tag, blank=True)
    specs = models.ManyToManyField(Spec, blank=True)    
    attachments = models.ManyToManyField(Attachment, blank=True)

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        self.code = self.code.upper()
        super(Product, self).save(*args, **kwargs)

    def tax(self):
        return self.price_sales - self.price_notax

    def amount_stocked(self, amount=0):
        """Get or set the stocked amount of this product
        """
        if amount:
            amount = int(amount)
            Inventory.objects.filter(slot=self.id).delete()
            for _ in xrange(amount):
                i = Inventory.objects.create(slot=self.id, product=self)
        try:
            return Inventory.objects.filter(slot=self.id).count()
        except Exception, e:
            return 0

    def amount_ordered(self):
        """Get or set the ordered amount of this product
        """
        try:
            return Inventory.objects.filter(product=self.id, kind='po').count()
        except Exception, e:
            return 0

    def amount_reserved(self):
        """Get or set the reserved amount of this product
        """
        try:
            return Inventory.objects.filter(product=self.id, kind='order').count()
        except Exception, e:
            return 0
    
class GsxData(models.Model):
    key = models.CharField(max_length=128)
    value = models.TextField(blank=True)
    references = models.CharField(max_length=16)
    reference_id = models.IntegerField()

class GsxRepair(models.Model):
    #customer_data = DictField()
    symptom = models.TextField()
    diagnosis = models.TextField()

class Calendar(models.Model):
    title = models.CharField(default='Uusi kalenteri', max_length=128)
    user = models.ForeignKey(User)
    hours = models.IntegerField(default = 0)

    def events(self):
        return CalendarEvent.objects.filter(calendar=self)

class CalendarEvent(models.Model):
    started_at = models.DateTimeField(default = datetime.now())
    finished_at = models.DateTimeField(null=True)
    description = models.CharField(default='', max_length=255)
    hours = models.IntegerField(default = 8)
    calendar = models.ForeignKey(Calendar)

class Invoice(models.Model):
    PAYMENT_METHOS = (
        (0, u'Ei veloitusta'), (1, u'Käteinen'), (2, u'Lasku'),
        (3, u'Maksukortti'), (4, u'Postiennakko'), (5, u'Verkkomaksu'))
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.ForeignKey(User)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField()
    payment_method = models.CharField(max_length=128,
        choices=PAYMENT_METHOS,
        default=PAYMENT_METHOS[0])

    customer = models.ForeignKey(Customer)
    customer_info = models.TextField()

    total_tax = models.DecimalField(max_digits=4, decimal_places=2)
    total_margin = models.DecimalField(max_digits=4, decimal_places=2)
    total_sum = models.DecimalField(max_digits=4, decimal_places=2)

class InvoiceItem(Product):
    invoice = models.ForeignKey(Invoice)

class PurchaseOrder(models.Model):
    reference = models.CharField(max_length=32)
    confirmation = models.CharField(max_length=32)
    dispatch_id = models.CharField(max_length=32)
    sales_order = models.CharField(max_length=32)

    date_created = models.DateTimeField(default = datetime.now(),
        editable=False)
    date_ordered = models.DateTimeField(default = datetime.now())
    date_arrived = models.DateTimeField(blank=True, editable=False)
    
    carrier = models.CharField(max_length=32, blank=True)
    supplier = models.CharField(max_length=32, blank=True)
    tracking_id = models.CharField(max_length=128, blank=True)
    days_delivered = models.IntegerField(blank=True)

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

    def __unicode__(self):
        return self.title

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
    title = models.CharField(default='Uusi jono', max_length=255)
    description = models.TextField(blank=True)
    gsx_account = models.ForeignKey(GsxAccount, null=True)
    
    order_template = models.ForeignKey(Attachment,
        related_name='order_template', null=True)
    receipt_template = models.ForeignKey(Attachment,
        related_name='receipt_template', null=True)
    dispatch_template = models.ForeignKey(Attachment,
        related_name='dispatch_template', null=True)

    statuses = models.ManyToManyField(Status, through='QueueStatus')

    def __unicode__(self):
        return self.title

class QueueStatus(models.Model):
    limit_green = models.IntegerField()
    limit_yellow = models.IntegerField()
    limit_factor = models.IntegerField()
    queue = models.ForeignKey(Queue)
    status = models.ForeignKey(Status)

class Order(models.Model):
    class Meta:
        ordering = ['-priority', 'id']

    PRIORITIES = ((0, 'Matala'), (1, 'Normaali'), (2, 'Korkea'))
    priority = models.IntegerField(default=1, choices=PRIORITIES,
        verbose_name=u'Prioriteetti')
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.ForeignKey(User, related_name='created_by')

    closed_at = models.DateTimeField(null=True)
    followed_by = models.ManyToManyField(User, related_name='followed_by')

    user = models.ForeignKey(User, null=True, verbose_name=u'Käsittelijä')
    tags = models.ManyToManyField(Tag)

    customer = models.ForeignKey(Customer, null=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    devices = models.ManyToManyField(Device)

    queue = models.ForeignKey(Queue, null=True, verbose_name=u'Jono')
    status = models.ForeignKey(Status, null=True, verbose_name=u'Status')

    STATES = ((0, 'unassigned'), (1, 'open'), (2, 'closed'))
    state = models.IntegerField(default = 0, max_length=16, choices=STATES)

    status_limit_green = models.IntegerField(null=True)   # timestamp in seconds
    status_limit_yellow = models.IntegerField(null=True)  # timestamp in seconds
    
    attachments = models.ManyToManyField(Attachment)
    #gsx_repairs = models.TextField(DictField())

    DISPATCH_METHODS = ((0, 'Ei toimitusta'), (1, 'Nouto'), (2, 'Posti'), (3, 'Kuriiri'))
    dispatch_method = models.IntegerField(choices=DISPATCH_METHODS,
        default=1, verbose_name=u'Toimitustapa')

    def notes(self):
        return Note.objects.filter(order=self)

    def messages(self):
        return Message.objects.filter(order=self)

    def events(self):
        return Event.objects.filter(order=self)

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
            return 'Ei statusta'

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
                return 'green'
            if time() < self.status_limit_yellow:
                return 'yellow'
            if time() > self.status_limit_yellow:
                return 'red'
  
    def customer_id(self):
        return self.customer.id
  
    def device_name(self):
        name = 'Ei laitetta'
        if self.devices.count():
            name = self.devices.all()[0].description

        return name
    
    def customer_name(self):
        try:
            name = self.customer.name
        except Exception, e:
            name = 'Ei asiakasta'
        
        return name
    
    def device_spec(self):
        if self.devices.count():
            return self.devices.all()[0].spec.id

class PurchaseOrderItem(models.Model):
    code = models.CharField(max_length=128)
    amount = models.IntegerField()
    service_order = models.ForeignKey(Order, null=True)
    purchase_order = models.ForeignKey(PurchaseOrder)

class Event(models.Model):
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime.now())
    handled_at = models.DateTimeField(null=True)
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User)
    kind = models.CharField(max_length=32)

class Issue(models.Model):
    class Meta:
        ordering = ['id']
    
    symptom = models.TextField()
    diagnosis = models.TextField()
    solution = models.TextField()

    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(default=datetime.now(), editable=False)
    order = models.ForeignKey(Order, editable=False)

class Message(models.Model):
    class Meta:
        ordering = ['id']
    
    body = models.TextField()
    subject = models.CharField(max_length=255)

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
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        conf = Configuration.objects.get(pk=1)
        subject = 'Huoltotilaus SRV#%d' %(self.order.id)

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = conf.mail_from
        msg['To'] = self.mailto
        msg.preamble = self.body

        txt = MIMEText(self.body)
        msg.attach(txt)

        for f in self.attachments.all():
            maintype, subtype = f.content_type.split('/', 1)
            a = MIMEBase(maintype, subtype)
            a.set_payload(f.content.read())
            msg.attach(a)

        server = smtplib.SMTP(conf.smtp_host)
        server.sendmail(conf.mail_from, self.mailto, msg.as_string())
        server.quit()
    
    def send_sms(self):
        import urllib
        conf = Configuration.objects.get(pk=1)
        params = urllib.urlencode({
            'username': conf.sms_user,
            'password': conf.sms_password,
            'text': self.body,
            'to': self.smsto
        })

        f = urllib.urlopen('%s?%s' %(conf.sms_url, params))
        print f.read()

class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    sn = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    reported = models.BooleanField(default=True)

class Search(models.Model):
    query = models.TextField()
    model = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    shared = models.BooleanField(default=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    tech_id = models.CharField(max_length=16, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    location = models.ForeignKey(Location)
    locale = models.CharField(max_length=8)
    