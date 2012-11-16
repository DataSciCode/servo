#coding=utf-8

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import pre_save, post_save
from django.utils.translation import ugettext as _
from django.dispatch import receiver
from django.core.cache import cache

from servo.models import Location, Queue

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    queues = models.ManyToManyField(Queue, verbose_name=_(u'jonot'))
    location = models.ForeignKey(Location, null=True, 
    	verbose_name=_(u'jonot'))
    tech_id = models.CharField(max_length=16, blank=True)
    phone = models.CharField(max_length=16, blank=True, 
    	verbose_name=_(u'puhelin'))

    LOCALES = (
        ('fi_FI.UTF-8', _('Suomi')),
        ('en_GB.UTF-8', _('English')),
    )

    locale = models.CharField(max_length=32, choices=LOCALES)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
