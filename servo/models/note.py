#coding=utf-8

import re
from django.db import models
from datetime import datetime
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from servo.lib.shorturl import encode_url, from_time

from django.contrib.auth.models import User, Group

from servo.models.order import Order
from servo.models.common import Attachment, Configuration

class Note(MPTTModel):
    subject = models.CharField(max_length=255, blank=True, 
        verbose_name=_(u'otsikko'))
    body = models.TextField(verbose_name=_(u'viesti'))
    code = models.CharField(max_length=8, editable=False, default=from_time())
    sender = models.CharField(max_length=64, null=True, blank=True,
        verbose_name=_(u'lähettäjä'))
    recipient = models.CharField(max_length=255, null=True, blank=True, 
        verbose_name=_(u'saaja'))

    KINDS = (
        ('note', _(u'Merkintä')),
        ('problem', _(u'Ongelma')),
        ('diagnosis', _(u'Diagnoosi')),
        ('solution', _(u'Ratkaisu')),
        ('message', _(u'Viesti'))
    )

    kind = models.CharField(max_length=10, choices=KINDS, default=KINDS[0])
    parent = TreeForeignKey('self', null=True, blank=True, related_name='replies')
    
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(default=datetime.now(), editable=False)
    sent_at = models.DateTimeField(null=True, editable=False)

    order = models.ForeignKey(Order, null=True, blank=True)
    flags = models.CharField(max_length=2, default='01', blank=True)

    should_report = models.BooleanField(default=True, verbose_name=_(u'raportoi'))
    attachments = models.ManyToManyField(Attachment, null=True, blank=True)

    def smsto(self):
        """Return the recipient's SMS address"""
        match = re.search(r'<([\+\d+])>$', self.recipient)
        if match:
            return match.group(1)

    def mailto(self):
        """Return the recipient's email address"""
        match = re.search("<(.+@.+)>$", self.recipient)
        if match:
            return match.group(1)

    def diagnosis(self):
        """
        Returns the diagnosis for this problem, if any
        """
        try:
            diag = Note.objects.get(parent=self)
            return diag.body
        except Note.DoesNotExist:
            return ""

    def solution(self):
        return ""

    def send_mail(self):
        import smtplib
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        conf = Configuration.conf()
        server = smtplib.SMTP(conf['smtp_host'])

        if conf['smtp_user']:
            server.login(conf['smtp_user'], conf['smtp_password'])
        
        subject = 'Huoltoviesti SRV#%s' %(self.code)

        msg = MIMEMultipart()
        msg['To'] = self.mailto()
        msg['Subject'] = subject
        msg['From'] = conf['mail_from']
        msg['In-Reply-To'] = str(self.code)
        
        txt = MIMEText(self.body, 'plain', 'utf-8')
        msg.attach(txt)
        
        for f in self.attachments.all():
            maintype, subtype = f.content_type.split('/', 1)
            a = MIMEBase(maintype, subtype)
            a.set_payload(f.content.read())
            encoders.encode_base64(a)
            msg.add_header('Content-Disposition', 'attachment', filename=f.name)
            msg.attach(a)

        self.sent_at = datetime.now()
        self.save()

        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    
    def send_sms(self):
        import urllib
        conf = Configuration.conf()
        params = urllib.urlencode({
            'username': conf['sms_user'],
            'password': conf['sms_password'],
            'text': self.body,
            'to': self.smsto
        })

        f = urllib.urlopen('%s?%s' %(conf.sms_url, params))
        self.sent_at = datetime.now()
        self.save()

        print f.read()

    def __str__(self):
        return str(self.pk)

    class Meta:
        app_label = 'servo'

@receiver(post_save, sender=Note)
def send_message(sender, instance, created, **kwargs):
    if instance.mailto() and not instance.sent_at:
        from django.core.validators import validate_email, ValidationError, RegexValidator
        try:
            validate_email(instance.mailto())
            instance.send_mail()
        except ValidationError:
            print "Invalid recipient: %s" %instance.recipient
            
        if instance.smsto():
            instance.send_sms()
