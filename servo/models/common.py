#coding=utf-8

from django.db import models
from datetime import datetime

from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _

from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User, Group
from django_countries import CountryField

from servo.lib.shorturl import encode_url
from servo.models.gsx import GsxAccount

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

    title = models.CharField(default=_('Uusi tagi'), max_length=255,
        unique=True,
        verbose_name=_(u'nimi'))
    type = models.CharField(max_length=32, choices=TYPES, 
        verbose_name=_(u'tyyppi'))
    times_used = models.IntegerField(default=0, editable=False)
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')

    def get_absolute_url(self):
        return "/admin/tags/%s/" % self.pk

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'servo'

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

    class Meta:
        app_label = 'servo'

class Location(models.Model):
    title = models.CharField(max_length=255, default=_('Uusi sijainti'),
        verbose_name=_(u'nimi'))
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
    country = CountryField(verbose_name=_(u'maa'))
    office_hours = models.CharField(max_length=16, null=True, blank=True,
        verbose_name=_(u'aukioloajat'), default='9:00 - 18:00')

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'servo'

class Configuration(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def conf(cls, key=None):
        if cache.get('config'):
            return cache.get('config')

        config = dict()
        
        for r in Configuration.objects.all():
            config[r.key] = r.value

        cache.set('config', config)

        return config.get(key) if key else config

    class Meta:
        app_label = 'servo'

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

    class Meta:
        app_label = 'servo'

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

    class Meta:
        app_label = 'servo'

class Search(models.Model):
    query = models.TextField()
    model = models.CharField(max_length=32)
    title = models.CharField(max_length=128)
    shared = models.BooleanField(default=True)

    class Meta:
        app_label = 'servo'

class Event(models.Model):
    """
    An event is something that happens.
    """
    description = models.CharField(max_length=255)
    triggered_by = models.ForeignKey(User)
    triggered_at = models.DateTimeField(default=datetime.now())
    handled_at = models.DateTimeField(null=True)
    
    ref = models.CharField(max_length=32)       # name of table the event references
    ref_id = models.CharField(max_length=32)    # id
    action = models.CharField(max_length=32)

    class Meta:
        ordering = ('-id',)
        app_label = 'servo'

    def get_icon(self):
        return "event-%s-%s" %(self.ref, self.action)

class Notification(models.Model):
    """
    A notification is a user-configurable response to an event
    """
    KINDS = (('order', 'Tilaus'), ('note', 'Merkintä'))
    ACTIONS = (('created', 'Luotu'), ('edited', 'Muokattu'))

    kind = models.CharField(max_length=16)
    action = models.CharField(max_length=16)
    message = models.TextField()

    class Meta:
        app_label = 'servo'

class Template(models.Model):
    title = models.CharField(max_length=128, blank=False,
        verbose_name=_(u'otsikko'), default=_(u'Uusi pohja'))
    content = models.TextField(blank=False, verbose_name=_(u'teksti'))

    def get_absolute_url(self):
        return "/notes/templates/%d/" % self.pk

    class Meta:
        app_label = 'servo'

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

    def as_dict(self, queue):
        print queue.queuestatus_set
        result = dict()
        result['enabled'] = False
        result['title'] = self.title
        result['limit_green'] = self.limit_green
        result['limit_yellow'] = self.limit_yellow
        result['limit_factor'] = self.limit_factor
        return result

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = 'servo'

class Queue(models.Model):
    title = models.CharField(unique=True, max_length=255, 
        default=_('Uusi jono'),
        verbose_name=_('nimi'))
    
    description = models.TextField(blank=True, verbose_name=_('kuvaus'))
    gsx_account = models.ForeignKey(GsxAccount, null=True, blank=True,
        verbose_name=_(u'GSX tili'))

    statuses = models.ManyToManyField(Status, through='QueueStatus')

    order_template = models.FileField(blank=True, null=True, 
        upload_to='queues',
        verbose_name=_(u'tilauspohja'))

    receipt_template = models.FileField(null=True, blank=True, 
        upload_to='queues',
        verbose_name=_(u'kuittipohja'))

    dispatch_template = models.FileField(null=True, blank=True,
        upload_to='queues',
        verbose_name=_(u'lähetepohja'))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
        app_label = 'servo'

class QueueStatus(models.Model):
    """
    This allows us to set time limits for each status per indiviudal queue
    """
    limit_green = models.IntegerField()
    limit_yellow = models.IntegerField()
    limit_factor = models.IntegerField()
    queue = models.ForeignKey(Queue)
    status = models.ForeignKey(Status)

    def __str__(self):
        return self.status.title

    class Meta:
        app_label = 'servo'