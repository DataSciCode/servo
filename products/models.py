#coding=utf-8

from decimal import *
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _
from django.core.cache import cache

from servo.models import Tag, Attachment, Configuration

class ProductGroup(MPTTModel):
    name = models.CharField(max_length=255, verbose_name=_(u'nimi'),
        default=_(u'Uusi ryhmä'))
    description = models.TextField(max_length=255, null=True, blank=True,
        verbose_name=_(u'kuvaus'))
    parent = TreeForeignKey('self', null=True, blank=True, 
        related_name='children')

    def __unicode__(self):
        return self.name

class BaseProduct(models.Model):
    def default_vat():
        conf = Configuration.conf()
        return conf.get('pct_vat', 0.0)

    def default_margin():
        conf = Configuration.conf()
        return conf.get('pct_margin', 0.0)
    
    title = models.CharField(max_length=255, default=_(u'Uusi tuote'),
        verbose_name=_(u'nimi'))
    code = models.CharField(max_length=32, unique=True,
        verbose_name = _(u'koodi'))
    description = models.TextField(blank=True, null=True,
        verbose_name=_(u'kuvaus'))
    pct_vat = models.DecimalField(decimal_places=2, max_digits=4,
        default=default_vat,
        verbose_name = _(u'verokanta'))
    pct_margin = models.DecimalField(decimal_places=2, max_digits=4, 
        default=default_margin,
        verbose_name=_(u'kate %'))
    price_notax = models.DecimalField(default=0, max_digits=6, decimal_places=2, 
        verbose_name=_(u'veroton hinta'))
    price_sales = models.DecimalField(default=0, max_digits=6, decimal_places=2,
        verbose_name=_(u'myyntihinta'))
    price_purchase = models.DecimalField(default=0, decimal_places=2,
        max_digits=6,
        verbose_name=_(u'ostohinta'))
    price_exchange = models.DecimalField(default=0, decimal_places=2,
        max_digits=6,
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
    group = models.ForeignKey(ProductGroup, null=True, blank=True,
        verbose_name=_(u'tuoteryhmä'))

    files = models.ManyToManyField(Attachment, blank=True, null=True,
        verbose_name=_(u'liitteet'))

    # component code is used to identify Apple parts
    component_code = models.CharField(max_length=1, blank=True, null=True,
        verbose_name=_(u'komponentti'))

    quantity_minimum = models.IntegerField(default=0,
        verbose_name=_(u'minimimäärä'))
    quantity_reserved = models.IntegerField(default=0,
        verbose_name=_(u'varattu'))
    quantity_stocked = models.IntegerField(default=0,
        verbose_name=_(u'varastossa'))
    quantity_ordered = models.IntegerField(default=0,
        verbose_name=_(u'tilattu'))

    class Meta:
        verbose_name = _(u'tuote')
        ordering = ['-id']

    def get_absolute_url(self):
        return "/products/%d/view/" % self.id

    @classmethod
    def from_gsx(self, gsx_data):
    	conf = Configuration.conf()
        getcontext().rounding = ROUND_UP

        sp = Decimal(gsx_data.get('stockPrice'))
        ep = Decimal(gsx_data.get('exchangePrice'))
        
        vat = Decimal(conf['pct_vat'])
        margin = Decimal(conf['pct_margin'])

        sp = (sp+(sp/100*margin)).quantize(Decimal('1.'))
        ep = (ep+(ep/100*margin)+(ep/100*vat)).quantize(Decimal('1.'))

        product = Product(code=gsx_data.get('partNumber'),
            title=gsx_data.get('partDescription'),
            price_purchase=gsx_data.get('stockPrice'),
            price_exchange=ep,
            pct_margin=margin,
            pct_vat=vat,
            price_notax=sp,
            warranty_period=3,
            brand='Apple',
            component_code=gsx_data.get('componentCode'),
            is_serialized=(gsx_data['isSerialized'] == "Y"),
            price_sales=sp+(sp/100*vat).quantize(Decimal('1.'))
        )

        return product

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        self.code = self.code.upper()
        super(Product, self).save(*args, **kwargs)

    def tax(self):
        return self.price_sales - self.price_notax

    def amount_stocked(self, amount=0):
        """
        Get or set the stocked amount of this product
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
        """
        Get or set the ordered amount of this product
        """
        try:
            return Inventory.objects.filter(product=self.id, kind='po').count()
        except Exception, e:
            return 0

    def amount_reserved(self):
        """
        Get or set the reserved amount of this product
        """
        try:
            return Inventory.objects.filter(product=self.id, kind='order').count()
        except Exception, e:
            return 0

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
        return PurchaseOrder.objects.get(pk=self.slot)
