from django.db import models
from django.utils.translation import ugettext as _

from django.contrib.auth.models import User

class Calendar(models.Model):
    title = models.CharField(default=_('Uusi kalenteri'), max_length=128)
    user = models.ForeignKey(User)
    hours = models.IntegerField(default=0)

class CalendarEvent(models.Model):
    started_at = models.DateTimeField(default=datetime.now())
    finished_at = models.DateTimeField(null=True)
    description = models.CharField(max_length=255)
    hours = models.IntegerField(default=8)
    calendar = models.ForeignKey(Calendar)
