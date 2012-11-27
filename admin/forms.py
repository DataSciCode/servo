# coding=utf-8

from django import forms
from servo.models import *
from products.models import *
from accounts.models import UserProfile
from django.utils.translation import ugettext as _

class TabbedForm(forms.Form):
    tabs = dict()

class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        exclude = ['statuses']

class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = ProductGroup

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag

class FieldForm(forms.ModelForm):
    class Meta:
        model = Property

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'user_permissions']

    location = forms.ModelChoiceField(queryset=Location.objects.all())
    locale = forms.ChoiceField(UserProfile.LOCALES)
    phone = forms.CharField(max_length=128, required=False, label=_(u'Puhelin'))
    tech_id = forms.CharField(max_length=128, required=False, label=_('Tech ID'))
    customer = forms.CharField(max_length=5)

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        widgets = {
            'permissions': forms.SelectMultiple(
                attrs={'style': 'height:400px;width:400px'}
            ),
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location

class GsxAccountForm(forms.ModelForm):
    class Meta:
        model = GsxAccount
    
    password = forms.CharField(widget=forms.PasswordInput)

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template

class SettingsForm(TabbedForm):
    company_name = forms.CharField(max_length=128, label=_('Yritys'))
    pct_margin = forms.DecimalField(max_digits=4, label=_('Kate %'))
    pct_vat = forms.DecimalField(max_digits=4, label=_('ALV %'))
    imap_host = forms.CharField(max_length=128, label=_('Palvelin'))
    imap_password = forms.CharField(max_length=128, label=_('Salasana'), 
        widget=forms.PasswordInput)
    imap_ssl = forms.BooleanField(label=_(u'Käytä salausta'))

    mail_from = forms.CharField(max_length=128, label=_('Osoite'))
    smtp_host = forms.CharField(max_length=128, label=_('Palvelin'))
    smtp_user = forms.CharField(max_length=128, label=_(u'Käyttäjä'))
    smtp_password = forms.CharField(max_length=128, label=_('Salasana'),
        widget=forms.PasswordInput)
    smtp_ssl = forms.BooleanField(label=_(u'Käytä salausta'))

    sms_url = forms.CharField(max_length=128, label=_('URL-osoite'))
    sms_user = forms.CharField(max_length=128, label=_(u'Käyttäjä'))
    sms_password = forms.CharField(max_length=128, label=_('Salasana'),
        widget=forms.PasswordInput)
    smtp_ssl = forms.BooleanField(label=_(u'Käytä salausta'))
