#coding=utf-8

from django.db import models
from datetime import datetime

from django.utils.translation import ugettext as _

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache

from lib.shorturl import encode_url

from django.contrib.auth.models import User, Group

from servo.models import *
from products.models import *
from customers.models import Customer
from devices.models import Device

class Order(models.Model):
    code = models.CharField(max_length=5, null=True, blank=True)
    PRIORITIES = ((0, 'Matala'), (1, 'Normaali'), (2, 'Korkea'))
    priority = models.IntegerField(default=1, choices=PRIORITIES,
        verbose_name=_(u'Prioriteetti'))
    created_at = models.DateTimeField(default=datetime.now())
    created_by = models.ForeignKey(User, related_name='created_by')

    closed_at = models.DateTimeField(null=True)
    followed_by = models.ManyToManyField(User, related_name='followed_by')

    tags = models.ManyToManyField(Tag, verbose_name=u'tagit')
    user = models.ForeignKey(User, null=True, verbose_name=u'käsittelijä')

    customer = models.ForeignKey(Customer, null=True)
    products = models.ManyToManyField(Product, through='ServiceOrderItem')
    devices = models.ManyToManyField(Device, null=True, blank=True)

    queue = models.ForeignKey(Queue, null=True, verbose_name=_(u'jono'))
    status = models.ForeignKey(Status, null=True, verbose_name=_(u'status'))

    STATES = ((0, 'unassigned'), (1, 'open'), (2, 'closed'))
    state = models.IntegerField(default = 0, max_length=16, choices=STATES)

    status_limit_green = models.IntegerField(null=True)   # timestamp in seconds
    status_limit_yellow = models.IntegerField(null=True)  # timestamp in seconds

    class Meta:
        ordering = ['-priority', 'id']

    def get_absolute_url(self):
        return "/orders/%d/" % self.pk

    def close(self, user):
        self.closed_at = datetime.now()
        self.state = 2
        self.save()

        Event.objects.create(description=_(u'Tilaus %d suljettu' %self.id),
            order=self, kind='close_order', user=user)

    def notes(self):
        return self.note_set.all()

    def reportable(self):
        return self.note_set.filter(report=True)

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
            return _(u'Ei statusta')

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
    
    def set_property(self, key, value):
        pass

    def set_status(self, status_id, user):
        from time import time
        status = Status.objects.get(pk=status_id)
        # calculate when this status will timeout
        green = (status.limit_green*status.limit_factor)+time()
        yellow = (status.limit_yellow*status.limit_factor)+time()
        self.status_limit_green = green
        self.status_limit_yellow = yellow
        self.status = status
        self.save()

        Event.objects.create(description=status.title,
            order=self,
            kind='set_status',
            user=user)

    def set_queue(self, queue_id, user):
        queue = Queue.objects.get(pk=queue_id)
        self.queue = queue
        event = Event.objects.create(description=queue.title, order=self,
            kind='set_queue',
            user=user)

        self.save()

    def set_user(self, user_id, current_user):
        if user_id == '':
            user = None
            event = _(u'Käsittelijä poistettu')
            state = 0 # unassigned
        else:
            user = User.objects.get(pk=user_id)
            event = user.username
            state = 1 # open

        self.user = user
        self.state = state
        self.save()

        Event.objects.create(description=event, order=self, kind='set_user',
            user=current_user)

    def customer_id(self):
        return self.customer.id
    
    def customer_tree(self):
        if self.customer is None:
            return '0'
        else:
            return self.customer.tree_id

    def device_name(self):
        name = _(u'Ei laitetta')
        if self.devices.count():
            name = self.devices.all()[0].description

        return name
    
    def customer_name(self):
        try:
            name = self.customer.name
        except AttributeError:
            name = _(u'Ei asiakasta')
        
        return name
    
    def device_tag(self):
        if self.devices.count() < 1:
            return 0
        try:
            return self.devices.all()[0].tags.all()[0].id
        except AttributeError:
            return 0

    def issues(self):
        return self.note_set.filter(kind='problem')

    def net_total(self):
        total = 0

        for p in self.serviceorderitem_set.filter(reported=True):
            total += (p.price * p.amount())

        return total

    def add_product(self, product, amount=1):
        Inventory.objects.filter(slot=self.pk, product=product).delete()
        i = 0

        while i < amount:
            Inventory.objects.create(slot=self.pk, product=product, kind='order')
            i = i + 1

        oi = ServiceOrderItem.objects.create(order=self, product=product,
            title=product.title,
            price=product.price_sales)

        self.save()

class OrderItem(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=128, verbose_name=_(u'nimi'))
    description = models.TextField(blank=True, null=True,
        verbose_name=_(u'kuvaus'))

    class Meta:
        abstract = True

class ServiceOrderItem(OrderItem):
    order = models.ForeignKey(Order)
    dispatched = models.BooleanField(default=False, verbose_name=_(u'toimitettu'))
    sn = models.CharField(max_length=32, null=True, blank=True,
        verbose_name=_(u'sarjanumero'))
    reported = models.BooleanField(default=True, verbose_name=_(u'raportoi'))
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'myyntihinta'))

    def amount(self):
        i = Inventory.objects.filter(slot=self.order.pk, product=self.product)
        return i.count()

class Event(models.Model):
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=datetime.now())
    handled_at = models.DateTimeField(null=True)
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User)
    kind = models.CharField(max_length=32)

    class Meta:
        ordering = ['-id']

class Invoice(models.Model):
    PAYMENT_METHOS = (
        (0, _(u'Ei veloitusta')),
        (1, _(u'Käteinen')),
        (2, _(u'Lasku')),
        (3, _(u'Maksukortti')),
        (4, _(u'Postiennakko')),
        (5, _(u'Verkkomaksu'))
	)

    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(default=datetime.now())
    payment_method = models.IntegerField(choices=PAYMENT_METHOS,
        default=PAYMENT_METHOS[0], verbose_name=_(u'maksutapa'))

    order = models.ForeignKey(Order)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)

    customer_name = models.CharField(max_length=128, default=_(u'Käteisasiakas'),
        verbose_name=_(u'asiakas'))
    customer_phone = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'puhelin'))
    customer_email = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'sähköposti'))
    customer_address = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'osoite'))

    total_tax = models.DecimalField(max_digits=6, decimal_places=2,
        editable=False)
    total_sum = models.DecimalField(max_digits=6, decimal_places=2,
        editable=False)
    total_margin = models.DecimalField(max_digits=6, decimal_places=2,
        editable=False)

    is_paid = models.BooleanField(default=False, verbose_name=_(u'maksettu'))
    paid_at = models.DateTimeField()

class InvoiceItem(OrderItem):
    invoice = models.ForeignKey(Invoice)
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'myyntihinta'))

class PurchaseOrder(models.Model):
    sales_order = models.CharField(max_length=32,
        verbose_name=_(u'huoltotilaus'))
    reference = models.CharField(max_length=32,
        verbose_name=_(u'viite'))
    confirmation = models.CharField(max_length=32,
        verbose_name=_(u'vahvistus'))

    created_by = models.ForeignKey(User)
    date_created = models.DateTimeField(default=datetime.now(), editable=False)
    date_submitted = models.DateTimeField(null=True, editable=False)

    supplier = models.CharField(max_length=32, blank=True, 
        verbose_name=_(u'toimittaja'))
    carrier = models.CharField(max_length=32, blank=True, 
        verbose_name=_(u'toimitustapa'))
    tracking_id = models.CharField(max_length=128, blank=True, 
        verbose_name=_(u'lähetystunnus'))
    days_delivered = models.IntegerField(blank=True, default=1, 
        verbose_name=_(u'toimitusaika'))

    def get_absolute_url(self):
        return "/products/po/%d/" % self.id

    def sum(self):
        total = 0
        for p in self.purchaseorderitem_set.all():
            total += float(p.price*p.quantity)
        return total

    def amount(self):
        amount = 0
        for p in self.purchaseorderitem_set.all():
            amount += p.quantity
        
        return amount

    def submit(self):
        self.date_submitted = datetime.now()
        self.save()
        for i in self.purchaseorderitem_set.all():
            Inventory.objects.create(kind='po', product=i.product, slot=self.id)

    def add_product(self, product, quantity=1):
        PurchaseOrderItem.objects.create(code=product.code,
            quantity=quantity,
            purchase_order=self,
            product_id=product.id, 
            price=product.price_purchase)
        
        for i in xrange(0, quantity):
            Inventory.objects.create(product=product, slot=self.id, kind="po")

class PurchaseOrderItem(OrderItem):
    code = models.CharField(max_length=128)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'ostohinta'))

    purchase_order = models.ForeignKey(PurchaseOrder, editable=False,
        verbose_name=_(u'ostotilaus'))
    order_item = models.ForeignKey(ServiceOrderItem, null=True, editable=False)

    date_ordered = models.DateTimeField(null=True, editable=False)
    date_arrived = models.DateTimeField(null=True, blank=True, editable=False,
        verbose_name=_(u'saapunut'))

class CheckList(models.Model):
    pass

class CheckListItem(models.Model):
    pass

class GsxRepair(models.Model):
    #customer_data = DictField()
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)

    symptom = models.TextField()
    diagnosis = models.TextField()

@receiver(post_save, sender=Order)
def trigger_event(sender, instance, created, **kwargs):
    if created:
    	instance.code = encode_url(instance.id).upper()
        Event.objects.create(description=_('Tilaus luotu'),
        	order=instance, 
        	kind='create_order',
            user=instance.created_by)

        instance.save()
