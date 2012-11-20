# coding=utf-8

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import ugettext as _

from servo.models import Tag
from devices.models import Device

class Customer(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, 
        related_name='contacts',
        limit_choices_to={'is_company': True},
        verbose_name=_(u'yritys'))
    name = models.CharField(default=_(u'Uusi asiakas'), max_length=255,
        verbose_name=_(u'nimi'))

    email = models.EmailField(null=True, blank=True, 
        verbose_name=_(u'sähköposti'))
    phone = models.CharField(max_length=32, null=True, blank=True, 
        verbose_name=_(u'puhelin'))
    street_address = models.CharField(max_length=128, null=True, blank=True, 
        verbose_name=_(u'katuosoite'))
    zip_code = models.CharField(max_length=32, null=True, blank=True, 
        verbose_name=_(u'postinumero'))
    city = models.CharField(max_length=32, null=True, blank=True,
        verbose_name=_(u'toimipaikka'))
    tags = models.ManyToManyField(Tag, blank=True, null=True,
        limit_choices_to = {'type': 'customer'},
        verbose_name=_(u'tagit'))
    devices = models.ManyToManyField(Device, null=True, blank=True, 
        verbose_name=_(u'laitteet'), editable=False)

    photo = models.ImageField(upload_to="photos", null=True, blank=True,
        verbose_name=_(u'kuva'))
    
    is_company = models.BooleanField(default=False, verbose_name=_(u'yritys'))

    class Meta:
        ordering = ['id']
    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/customers/%d/" % self.pk

    def gsx_address(self):
        """
        Return a dictionary that's compatibly with GSX's Address datatype
        """
        import re
        out = dict()
        for p in self.contactinfo_set.all():
            v = p.value
            if re.search('@', v):
                out['emailAddress'] = v
            if re.search('^\d{5}$', v):
                out['zipCode'] = v
            if re.search('^\d{6,}$', v):
                out['primaryPhone'] = v
            if re.search('^\w+\s\d+', v):
                out['adressLine1'] = v
            if re.search('^[A-Za-z]+$', v):
                out['city'] = v

        (out['firstName'], out['lastName']) = self.name.split(" ", 1)

        return out

    def get_property(self, key):
        """
        Return the value of a specific property
        """
        result = None
        ci = ContactInfo.objects.filter(customer=self)
        for i in ci:
            if i.key == key:
                result = i.value

        return result

    def fullname(self):
        """
        Get the entire info tree for this customer, upwards
        """
        return self.name
        title = []
        for c in self.path.split('.'):
            if c.isdigit():
                customer = Customer.objects.get(pk=c)
                title.append(customer.name)

        title.reverse()

        return str(', ').join(title)

    def fullprops(self):
        """
        Get the combined view of all the properties for this customer
        """
        props = {}
        for r in self.contactinfo_set.all():
            props[r.key] = r.value

        return props

class ContactInfo(models.Model):
    customer = models.ForeignKey(Customer)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
