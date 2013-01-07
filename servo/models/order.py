#coding=utf-8

from django.db import models
from datetime import datetime

from django.utils.translation import ugettext as _

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.cache import cache

from servo.lib.shorturl import encode_url

from django.contrib.auth.models import User, Group

from servo.models.common import *
from servo.models.product import *
from servo.models.customer import Customer
from servo.models.device import Device

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
        app_label = 'servo'

    def get_absolute_url(self):
        return '/orders/order/%d' % self.pk

    def close(self, user):
        self.closed_at = datetime.now()
        self.state = 2
        self.save()

        Event.objects.create(description=_(u'Tilaus %d suljettu' %self.id),
            ref='order', 
            ref_id=self.id, 
            action='close_order', 
            triggered_by=user)

    def notes(self):
        return self.note_set.all()

    def reportable(self):
        return self.note_set.filter(report=True)

    def events(self):
        return Event.objects.filter(ref="order", ref_id=self.pk)

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

    def notify(self, action, message, user):
        Event.objects.create(
            description=message,
            ref='order',
            ref_id=self.pk,
            action=action,
            triggered_by=user)

    def set_status(self, status_id, user):
        """Sets status of this order to status_id"""
        from time import time

        if isinstance(status_id, QueueStatus):
            status = status_id
        else:
            status = QueueStatus.objects.get(pk=status_id).status

        # calculate when this status will timeout
        green = (status.limit_green*status.limit_factor)+time()
        yellow = (status.limit_yellow*status.limit_factor)+time()
        self.status_limit_green = green
        self.status_limit_yellow = yellow
        self.status = status.status
        self.save()

        self.notify('set_status', status.status.title, user)

    def set_queue(self, queue_id, user):
        queue = Queue.objects.get(pk=queue_id)
        self.queue = queue
        self.notify('set_queue', queue.title, user)

        if queue.default_status:
            status = QueueStatus.objects.get(status=queue.default_status, queue=queue)
            self.set_status(status, user)
        else:
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

        Event.objects.create(description=event, ref='order',
            ref_id=self.id,
            action='set_user',
            triggered_by=current_user)

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

        for p in self.serviceorderitem_set.filter(should_report=True):
            total += p.product.price_notax * p.amount

        return total

    def gross_total(self):
        total = 0

        for p in self.serviceorderitem_set.filter(should_report=True):
            total += p.price * p.amount

        return total

    def total_tax(self):
        return self.gross_total() - self.net_total()

    def add_product(self, product, amount=1):
        Inventory.objects.filter(slot=self.pk, product=product).delete()
        i = 0

        while i < amount:
            Inventory.objects.create(slot=self.pk, product=product, kind='order')
            i = i + 1

        oi = ServiceOrderItem.objects.create(
            order=self,
            product=product,
            code=product.code,
            title=product.title,
            price=product.price_sales)

        self.save()
        return oi

    def dispatch(self, products):
        print products

    def total_margin(self):
        total_purchase_price = 0
        for p in self.serviceorderitem_set.filter(should_report=True):
            total_purchase_price += p.product.price_purchase * p.amount

        return (self.net_total() - total_purchase_price)

    def __str__(self):
        return 'Order #%d' % self.pk

class OrderItem(models.Model):
    product = models.ForeignKey(Product)
    code = models.CharField(max_length=128, blank=True, null=True)
    title = models.CharField(max_length=128, verbose_name=_(u'nimi'))
    description = models.TextField(blank=True, null=True,
        verbose_name=_(u'kuvaus'))
    amount = models.IntegerField(default=1, verbose_name=_(u'määrä'))
    sn = models.CharField(max_length=32, null=True, blank=True,
        verbose_name=_(u'sarjanumero'))

    class Meta:
        abstract = True

class ServiceOrderItem(OrderItem):
    """
    A product that has been added to a Service Order
    """
    order = models.ForeignKey(Order)
    dispatched = models.BooleanField(default=False, 
        verbose_name=_(u'toimitettu'))
    should_report = models.BooleanField(default=True, 
        verbose_name=_(u'raportoi'))
    should_return = models.BooleanField(default=False, 
        verbose_name=_(u'palautetaan'))
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'myyntihinta'))

    PRICE_CATEGORIES = (
        ('warranty', _(u'Takuu')),
        ('exchange', _(u'Vaihto')),
        ('stock', _(u'Stock')),
        )
    
    price_category = models.CharField(max_length=32, choices=PRICE_CATEGORIES,
        default=PRICE_CATEGORIES[0])

    def total_net(self):
        return self.product.price_notax * self.amount

    def total_tax(self):
        return (self.price - self.product.price_notax) * self.amount

    def total_gross(self):
        return self.price * self.amount

    class Meta:
        app_label = 'servo'

class Invoice(models.Model):
    PAYMENT_METHODS = (
        (0, _(u'Ei veloitusta')),
        (1, _(u'Käteinen')),
        (2, _(u'Lasku')),
        (3, _(u'Maksukortti')),
        (4, _(u'Postiennakko')),
        (5, _(u'Verkkomaksu'))
	)

    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(default=datetime.now())
    payment_method = models.IntegerField(choices=PAYMENT_METHODS,
        default=PAYMENT_METHODS[0], verbose_name=_(u'maksutapa'))
    is_paid = models.BooleanField(default=False, verbose_name=_(u'maksettu'))
    paid_at = models.DateTimeField(null=True, blank=True)

    order = models.ForeignKey(Order)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)

    # We remember the following the following so that the customer info
    # on the invoice doesn't change if the customer is modified or deleted
    customer_name = models.CharField(max_length=128, default=_(u'Käteisasiakas'),
        verbose_name=_(u'asiakas'))
    customer_phone = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'puhelin'))
    customer_email = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'sähköposti'))
    customer_address = models.CharField(max_length=128, blank=True, null=True,
        verbose_name=_(u'osoite'))

    total_net = models.DecimalField(max_digits=6, decimal_places=2)     # total w/o taxes
    total_gross = models.DecimalField(max_digits=6, decimal_places=2)   # total with taxes
    total_tax = models.DecimalField(max_digits=6, decimal_places=2)     # total taxes
    total_margin = models.DecimalField(max_digits=6, decimal_places=2)  # total margin


    def get_payment_method(self):
        return self.PAYMENT_METHODS[self.payment_method][1]

    class Meta:
        ordering = ('-id', )
        app_label = 'servo'

class InvoiceItem(OrderItem):
    invoice = models.ForeignKey(Invoice)
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'myyntihinta'))

    class Meta:
        app_label = 'servo'

class PurchaseOrder(models.Model):
    """
    A purchase order(PO) consists of different purchase order items 
    all of which may reference individual Service Orders. 
    When a PO is submitted, the included items are registered 
    to the /products/incoming/ list (items that have not yet arrived). 
    A PO cannot be edited after it's been submitted.
    
    Creating a PO from an SO only creates the PO, it does not submit it.
    """
    sales_order = models.ForeignKey(Order, null=True, blank=True,
        verbose_name=_(u'huoltotilaus'))
    reference = models.CharField(max_length=32, verbose_name=_(u'viite'),
        null=True, blank=True)
    confirmation = models.CharField(max_length=32, verbose_name=_(u'vahvistus'),
        null=True, blank=True)

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
    has_arrived = models.BooleanField(default=False)

    def get_absolute_url(self):
        return '/products/po/%d/' % self.id

    def sum(self):
        total = 0
        for p in self.purchaseorderitem_set.all():
            total += float(p.price*p.amount)
        return total

    def amount(self):
        amount = 0
        for p in self.purchaseorderitem_set.all():
            amount += p.amount
        
        return amount

    def submit(self):
        self.date_submitted = datetime.now()
        self.save()
        for i in self.purchaseorderitem_set.all():
            Inventory.objects.create(kind='po', product=i.product, slot=self.id)

    def add_product(self, product, amount=1):
        poi = PurchaseOrderItem(amount=amount, purchase_order=self)
        
        if isinstance(product, OrderItem):
            poi.code = product.product.code
            poi.order_item = product
            poi.price = product.price
            poi.product_id = product.product.id
        
        if isinstance(product, Product):
            poi.code = product.code
            poi.product_id = product.id
            poi.price = product.price_purchase

        poi.save()

        """
        PurchaseOrderItem.objects.create(code=product.code,
            amount=amount,
            purchase_order=self,
            product_id=product.id, 
            price=product.price_purchase)
        for i in xrange(0, amount):
            Inventory.objects.create(product=product, slot=self.id, kind='po')
        """

    class Meta:
        ordering = ('-id',)
        app_label = 'servo'

class PurchaseOrderItem(OrderItem):
    price = models.DecimalField(decimal_places=2, max_digits=6,
        verbose_name=_(u'ostohinta'))
    purchase_order = models.ForeignKey(PurchaseOrder, editable=False,
        verbose_name=_(u'ostotilaus'))
    order_item = models.ForeignKey(ServiceOrderItem, null=True, editable=False)
    date_ordered = models.DateTimeField(null=True, editable=False)
    date_received = models.DateTimeField(null=True, blank=True, editable=False,
        verbose_name=_(u'saapunut'))
    received_by = models.ForeignKey(User, null=True)

    class Meta:
        app_label = 'servo'

class CheckList(models.Model):
    pass

class CheckListItem(models.Model):
    pass

class GsxRepair(models.Model):
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)

    symptom = models.TextField()
    diagnosis = models.TextField()

@receiver(post_save, sender=Order)
def trigger_event(sender, instance, created, **kwargs):
    if created:
    	instance.code = encode_url(instance.id).upper()
        description = _('Tilaus %s luotu' % instance.code)
        instance.notify('created', description, instance.created_by)
        instance.save()

@receiver(post_save, sender=Invoice)
def trigger_order_dispatched(sender, instance, created, **kwargs):
    if created:
        description = _('Tilaus %s toimitettu' % instance.order.code)
        instance.order.notify('dispatched', description, instance.created_by)
    
        if instance.is_paid and not instance.paid_at:
            instance.paid_at = datetime.now()
            instance.save()

@receiver(post_save, sender=PurchaseOrderItem)
def trigger_product_ordered(sender, instance, created, **kwargs):
    product = instance.product
    
    if created:
        product.amount_ordered = product.amount_ordered + 1
        
    if instance.date_received:
        product.amount_ordered = product.amount_ordered - 1
        product.amount_stocked = product.amount_stocked + 1
        if instance.purchase_order.sales_order:
            message = _('Tuote %s saapunut' % instance.code)
            instance.purchase_order.sales_order.notify('arrived', message, 
                instance.received_by)

    product.save()

@receiver(post_save, sender=PurchaseOrder)
def trigger_purchase_order_created(sender, instance, created, **kwargs):
    if created and instance.sales_order:
        description = _(u'Ostotilaus %d luotu' % instance.id)
        Event.objects.create(description=description,
            ref='order',
            action='po_created',
            ref_id=instance.sales_order.id, 
            triggered_by=instance.created_by)
