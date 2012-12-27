#coding=utf-8
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_save, post_save

from servo.models.common import Tag, Attachment

class Device(models.Model):
    sn = models.CharField(max_length=32, blank=True, 
        verbose_name=_(u'sarjanumero'))
    description = models.CharField(max_length=128, default=_('Uusi laite'),
        verbose_name=_(u'kuvaus'))
    username = models.CharField(max_length=32, blank=True, null=True, 
        verbose_name=_(u'käyttäjätunnus'))
    password = models.CharField(max_length=32, blank=True, null=True, 
        verbose_name=_(u'salasana'))
    purchased_on = models.DateField(blank=True, null=True,
        verbose_name=_(u'hankittu'))
    notes = models.TextField(blank=True, null=True,
        verbose_name=_(u'merkinnät'))
    tags = models.ManyToManyField(Tag, null=True, blank=True, 
        verbose_name=_(u'tagit'))
    files = models.ManyToManyField(Attachment)

    def get_absolute_url(self):
        return "/devices/%d/view/" % self.pk

    def spec_id(self):
        return self.tags.all()[0].id

    def __unicode__(self):
        return '%s (%s)' %(self.description, self.sn)
        
    class Meta:
        app_label = 'servo'

@receiver(post_save, sender=Device)
def create_spec(sender, instance, created, **kwargs):
    # make sure we have this spec
    if created:
        (tag, created) = Tag.objects.get_or_create(title=instance.description, 
            type='device')
        instance.tags.add(tag)
        instance.save()
