#coding=utf-8

from decimal import *
from django.db import models
from django.core.cache import cache
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _
from servo.lib.gsx import gsx

from servo.models.common import Tag, Attachment, Configuration

class BaseProduct(models.Model):
    def default_vat():
        conf = Configuration.conf()
        return conf.get('pct_vat', 0.0)

    def default_margin():
        conf = Configuration.conf()
        return conf.get('pct_margin', 0.0)
    
    code = models.CharField(max_length=32, unique=True,
        verbose_name = _(u'koodi'), blank=True, null=True)
    title = models.CharField(max_length=255, default=_(u'Uusi tuote'),
        verbose_name=_(u'nimi'))
    
    description = models.TextField(blank=True, null=True,
        verbose_name=_(u'kuvaus'))

    pct_vat = models.DecimalField(decimal_places=2, max_digits=4,
        default=default_vat,
        verbose_name = _(u'verokanta'))
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4, 
        default=default_margin,
        verbose_name=_(u'kate %'))
    price_notax = models.DecimalField(default=0, max_digits=6, 
        decimal_places=2, 
        verbose_name=_(u'veroton hinta'))
    price_sales = models.DecimalField(default=0, max_digits=6, 
        decimal_places=2,
        verbose_name=_(u'myyntihinta'))
    price_purchase = models.DecimalField(default=0, max_digits=6,
        decimal_places=2,
        verbose_name=_(u'ostohinta'))
    price_exchange = models.DecimalField(default=0, max_digits=6,
        decimal_places=2,
        verbose_name=_(u'vaihtohinta'))
    is_serialized = models.BooleanField(default=False,
        verbose_name=_(u'sarjanumeroseuranta'))

    class Meta:
        abstract = True

class Product(BaseProduct):
    warranty_period = models.IntegerField(default=0,
        verbose_name=_(u'takuuaika'))
    shelf = models.CharField(default='', blank=True, max_length=8,
        verbose_name=_(u'hyllykoodi'))
    brand = models.CharField(default='', blank=True, max_length=32,
        verbose_name=_(u'valmistaja'))
    tags = models.ManyToManyField(Tag, blank=True, null=True,
    	limit_choices_to={'type': 'product', 'type': 'device'},
    	verbose_name=_(u'tagit'))
    files = models.ManyToManyField(Attachment, blank=True, null=True,
        verbose_name=_(u'liitteet'))

    # component code is used to identify Apple parts
    component_code = models.CharField(max_length=1, blank=True, null=True)
    amount_minimum = models.IntegerField(default=0,
        verbose_name=_(u'minimimäärä'))
    amount_reserved = models.IntegerField(default=0,
        verbose_name=_(u'varattu'))
    amount_stocked = models.IntegerField(default=0,
        verbose_name=_(u'varastossa'))
    amount_ordered = models.IntegerField(default=0,
        verbose_name=_(u'tilattu'))
    shipping = models.IntegerField(default=0,
        verbose_name=_(u'Shipping'))

    def get_absolute_url(self):
        return '/products/product/%d/' % self.pk

    @classmethod
    def from_gsx(cls, code, gsx_account):
        """
        Searches for a part from GSX and initializes Product
        with the data and our config
        """
    	conf = Configuration.conf()
        getcontext().rounding = ROUND_UP
        
        vat = Decimal(conf['pct_vat'])
        margin = Decimal(conf['pct_margin'])
        shipping = Decimal(conf['shipping_cost'])

        part = gsx.Part(partNumber=code).lookup()

        sp = Decimal(part.stockPrice)
        ep = Decimal(part.exchangePrice)
        sp = (sp+(sp/100*margin)).quantize(Decimal('1.')) + shipping
        ep = (ep+(ep/100*margin)+(ep/100*vat)).quantize(Decimal('1.')) + shipping

        product = Product(code=part.partNumber,
                        title=part.partDescription,
                        price_purchase=part.stockPrice,
                        price_exchange=ep,
                        pct_margin=margin,
                        pct_vat=vat,
                        price_notax=sp,
                        warranty_period=3,
                        brand='Apple',
                        shipping=conf['shipping_cost'],
                        component_code=part.componentCode,
                        is_serialized=(part.isSerialized == 'Y'),
                        price_sales=sp+(sp/100*vat).quantize(Decimal('1.'))
        )

        return product

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super(Product, self).save(*args, **kwargs)

    def tax(self):
        return self.price_sales - self.price_notax

    def latest_date_sold(self):
        return '-'

    def latest_date_ordered(self):
        return '-'

    def latest_date_arrived(self):
        return '-'

    def sell(self, amount=1):
        self.amount_stocked = self.amount_stocked - amount
        self.save()


    class Meta:
        verbose_name = _(u'tuote')
        ordering = ['-id']
        app_label = 'servo'

class Inventory(models.Model):
    """
    The Inventory tracks how many products are in each "slot".
    A slot can refer to basically any model in the system.
    The amount of stocked items is determined by the number of rows
    where slot points to itself.
    Product always points to a Product model.
    The reserved amount of a given item is determined 
    by the number of rows with the order id as slot
    """
    slot = models.IntegerField()
    product = models.ForeignKey(Product)
    sn = models.CharField(max_length=32, null=True)
    KINDS = ((0, 'po'), (1, 'order'), (2, 'product'), (3, 'invoice'))
    # one of "po", "order", "product" or "invoice"
    kind = models.CharField(max_length=32, choices=KINDS)

    def purchase_order(self):
        from orders.models import PurchaseOrder
        return PurchaseOrder.objects.get(pk=self.slot)

    class Meta:
        app_label = 'servo'
        