#coding=utf-8

from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext as _

from servo.lib.gsxlib.gsxlib import Gsx

class GsxObject(dict):
    def __init__(self, *args, **kwargs):
        for k, v in args[0].items():
            self[k] = v

class ServicePart(GsxObject):
    def title(self):
        return self['partDescription']

    def description(self):
        return self['partDescription']

    def code(self):
        return self['partNumber']

class GsxDevice(GsxObject):
    def title(self):
        pass

    def description(self):
        pass

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

    def get_absolute_url(self):
        return '/admin/gsx/accounts/%d/' % self.pk

    @classmethod
    def default(cls):
        """
        Return default GSX account and connect to it
        """
        act = GsxAccount.objects.get(is_default=True)
        return act.connect()

    def connect(self):
        gsx = Gsx(sold_to=self.sold_to, user_id=self.username, 
            password=self.password, environment=self.environment)
        cache.set('gsx', gsx, 60*25)

        return gsx

    class Meta:
        app_label = 'servo'

class Lookup(object):
    def __init__(self, *args, **kwargs):
        self.results = {}
        self.query = kwargs
        self.account = None

    def set_account(self, account):
        self.account = account

    def lookup(self):
        key, query = self.query.items()[0]

        if cache.get(query):
            return cache.get(query)

        if not self.account:
            self.account = GsxAccount.default()

        results = self.account.parts_lookup(self.query)

        for r in results:
            key = r['partNumber']
            self.results[key] = r

        cache.set_many(self.results, 60*20)
        return cache.get(query)

class Repair(models.Model):
    pass
    