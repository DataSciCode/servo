#coding=utf-8

from django.db import models
from datetime import datetime

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _

from django.dispatch import receiver
from django.core.cache import cache
from lib.shorturl import encode_url

from django.contrib.auth.models import User, Group

class GsxObject(object):
    def __init__(self, *args, **kwargs):
        for k, v in args[0].items():
            self.__setattr__(k, v)

class GsxDevice(GsxObject):
    def title(self):
        pass

    def description(self):
        pass

class ServicePart(GsxObject):
    def title(self):
        return self.partDescription

    def description(self):
        return self.partDescription

    def code(self):
        return self.partNumber

class Tag(MPTTModel):
    """
    A tag is a simple ine-word descriptor for something.
    The type attribute is used to group tags to make them easier
    to associate with different elements
    """
    class MPTTMeta:
        order_insertion_by = ['title']

    TYPES = (
        ('location', _(u'Sijainti')),
        ('order', _(u'Tilaus')),
        ('product', _(u'Tuote')),
        ('customer', _(u'Asiakas')),
        ('device', _(u'Laite')),
    )

    title = models.CharField(default=_('Uusi tagi'), max_length=255, unique=True,
        verbose_name=_(u'nimi'))
    type = models.CharField(max_length=32, choices=TYPES, 
        verbose_name=_(u'tyyppi'))
    times_used = models.IntegerField(default=0, editable=False)
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')

    def __unicode__(self):
        return self.title

class Attachment(models.Model):
    name = models.CharField(default=_(u'Uusi tiedosto'), max_length=255,
        verbose_name=_(u'nimi'))
    uploaded_by = models.CharField(max_length=32, editable=False)
    uploaded_at = models.DateTimeField(default=datetime.now(), editable=False)

    content = models.FileField(upload_to='attachments', 
        verbose_name=_(u'tiedosto'))
    content_type = models.CharField(max_length=64, editable=False)

    def __unicode__(self):
        return self.name

    def from_file(self, file):
        import mimetypes
        mimetypes.init()
        (type, encoding) = mimetypes.guess_type(file.name)
        self.content = file
        self.name = file.name
        self.content_type = type
        self.save()

class Location(models.Model):
    title = models.CharField(max_length=255, default=_('Uusi sijainti'),
        verbose_name=_(u'nimi'))
    description = models.TextField(blank=True, null=True, 
        verbose_name=_(u'kuvaus'))
    phone = models.CharField(max_length=32, blank=True, null=True,
        verbose_name=_(u'puhelin'))
    email = models.EmailField(blank=True, null=True, 
        verbose_name=_(u'sähköposti'))
    address = models.CharField(max_length=32, null=True, blank=True,
        verbose_name=_(u'osoite'))
    ship_to = models.CharField(max_length=32, null=True, blank=True)
    zip_code = models.CharField(max_length=8, null=True, blank=True,
        verbose_name=_(u'postinumero'))
    city = models.CharField(max_length=16, null=True, blank=True,
        verbose_name=_(u'toimipaikka'))

    def __unicode__(self):
        return self.title

class GsxAccount(models.Model):
    title = models.CharField(max_length=128, default=_('Uusi tili'),
        verbose_name=_(u'nimi'))

    sold_to = models.CharField(max_length=32, verbose_name=_(u'Sold-To'))
    ship_to = models.CharField(max_length=32, verbose_name=_(u'Ship-To'))
    username = models.CharField(max_length=64, verbose_name=_(u'tunnus'))
    password = models.CharField(max_length=64, verbose_name=_(u'salasana'))

    ENVIRONMENTS = (
        ('pr', _('Tuotanto')), 
        ('ut', _('Kehitys')),
        ('it', _('Testaus')),
    )

    environment = models.CharField(max_length=3, choices=ENVIRONMENTS,
        default=ENVIRONMENTS[0], 
        verbose_name=_(u'ympäristö'))

    is_default = models.BooleanField(default=True, verbose_name=_(u'oletus'))

    def __unicode__(self):
        return self.title

    @classmethod
    def default(self):
        """
        Return default GSX account and connect to it
        """
        from lib.gsxlib.gsxlib import Gsx

        act = GsxAccount.objects.get(is_default=True)
        gsx = Gsx(sold_to=act.sold_to, user_id=act.username, 
            password=act.password, environment=act.environment)

        cache.set('gsx', gsx, 60*25)
        return gsx

class Configuration(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def conf(key=None):
        if cache.get('config'):
            return cache.get('config')

        conf = dict()
        
        for r in Configuration.objects.all():
            conf[r.key] = r.value

        cache.set('config', conf)

        return conf.get("key") if key else conf

class Property(models.Model):
    TYPES = (
        ('customer', _(u'Asiakas')),
        ('order', _(u'Tilaus')),
        ('product', _(u'Tuote'))
        )

    title = models.CharField(max_length=255, verbose_name=_(u'otsikko'),
        default=_(u'Uusi kenttä'))

    type = models.CharField(max_length=32, choices=TYPES, default=TYPES[0],
        verbose_name=_(u'tyyppi'))

    format = models.CharField(max_length=32, blank=True, 
        verbose_name=_(u'muoto'))
    value = models.TextField(blank=True, null=True, verbose_name=_(u'arvo'))

    def __unicode__(self):
        return self.title

    def values(self):
        if self.value is None:
            return []
        else:
            return self.value.split(', ')

class Article(models.Model):
    """
    Wiki stuff...
    """
    title = models.CharField(default=_(u'Uusi artikkeli'), max_length=255)
    content = models.TextField()
    created_by = models.CharField(max_length=32)
    updated_at = models.DateTimeField()
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(default=datetime.now())
    attachments = models.ManyToManyField(Attachment)

class Search(models.Model):
    query = models.TextField()
    model = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    shared = models.BooleanField(default=True)
    
class Template(models.Model):
    title = models.CharField(max_length=128, blank=False,
        verbose_name=_(u'otsikko'))
    content = models.TextField(blank=False, verbose_name=_(u'teksti'))

class Status(models.Model):
    FACTORS = (
        (60, _(u'Minuuttia')),
        (3600, _(u'Tuntia')),
        (86400, _(u'Päivää')),
        (604800, _(u'Viikkoa')),
        (2419200, _('Kuukautta')),
    )

    title = models.CharField(unique=True, max_length=255, 
        default=_(u'Uusi status'),
        verbose_name=_(u'nimi'))
    description = models.TextField(blank=True, null=True,
        verbose_name=_(u'kuvaus'))
    limit_green = models.IntegerField(default=1, verbose_name=_(u'vihreä raja'))
    limit_yellow = models.IntegerField(default=15, 
        verbose_name=_(u'keltainen raja'))
    limit_factor = models.IntegerField(default=FACTORS[0], choices=FACTORS,
        verbose_name=_(u'aikayksikkö'))

    def __unicode__(self):
        return self.title

class Queue(models.Model):
    title = models.CharField(unique=True, max_length=255, default=_('Uusi jono'),
        verbose_name=_('nimi'))
    
    description = models.TextField(blank=True, verbose_name=_('kuvaus'))
    gsx_account = models.ForeignKey(GsxAccount, null=True, blank=True,
        verbose_name=_(u'GSX tili'))

    statuses = models.ManyToManyField(Status, through='QueueStatus')

    order_template = models.FileField(blank=True, null=True, upload_to='queues',
        verbose_name=_(u'tilauspohja'))

    receipt_template = models.FileField(null=True, blank=True, upload_to='queues',
        verbose_name=_(u'kuittipohja'))

    dispatch_template = models.FileField(null=True, blank=True,
        upload_to='queues',
        verbose_name=_(u'lähetepohja'))

    def __unicode__(self):
        return self.title

class QueueStatus(models.Model):
    limit_green = models.IntegerField()
    limit_yellow = models.IntegerField()
    limit_factor = models.IntegerField()
    queue = models.ForeignKey(Queue)
    status = models.ForeignKey(Status)
