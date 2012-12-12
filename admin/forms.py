# coding=utf-8

from django import forms
from servo.models import *
from products.models import *
from accounts.models import UserProfile
from django.utils.translation import ugettext as _

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
        widgets = {
            'limit_green': forms.TextInput(attrs={'class': 'input-mini'}),
            'limit_yellow': forms.TextInput(attrs={'class': 'input-mini'}),
        }

class QueueStatusForm(StatusForm):
    enabled = forms.IntegerField(widget=forms.CheckboxInput)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'user_permissions']

    password = forms.CharField(widget=forms.PasswordInput, label=_(u'Salasana'))
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    locale = forms.ChoiceField(UserProfile.LOCALES)
    phone = forms.CharField(max_length=128, required=False, 
        label=_(u'Puhelin'))
    tech_id = forms.CharField(max_length=128, required=False, 
        label=_('Tech ID'))
    customer = forms.CharField(max_length=5, required=False, 
        widget=forms.TextInput(attrs={'class': 'typeahead'}))

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

class SettingsForm(forms.Form):
    company_name = forms.CharField(max_length=128, label=_('Yritys'))
    pct_margin = forms.DecimalField(max_digits=4, label=_('Kate %'))
    pct_vat = forms.DecimalField(max_digits=4, label=_('ALV %'))

    mail_from = forms.CharField(max_length=128, label=_('Osoite'))
    imap_host = forms.CharField(max_length=128, label=_('Palvelin'))
    imap_user = forms.CharField(max_length=128, label=_('Tunnus'))
    imap_password = forms.CharField(max_length=128, label=_('Salasana'), 
        widget=forms.PasswordInput, required=False)
    imap_ssl = forms.BooleanField(label=_(u'Käytä salausta'), initial=True, 
        required=False)
    smtp_host = forms.CharField(max_length=128, label=_('Palvelin'), 
        required=False)
    smtp_user = forms.CharField(max_length=128, label=_(u'Tunnus'), 
        required=False)
    smtp_password = forms.CharField(max_length=128, label=_('Salasana'),
        widget=forms.PasswordInput, required=False)
    smtp_ssl = forms.BooleanField(label=_(u'Käytä salausta'), initial=True, 
        required=False)
    sms_url = forms.CharField(max_length=128, label=_('URL-osoite'), 
        required=False)
    sms_user = forms.CharField(max_length=128, label=_(u'Tunnus'), 
        required=False)
    sms_password = forms.CharField(max_length=128, label=_('Salasana'),
        widget=forms.PasswordInput, required=False)
    smtp_ssl = forms.BooleanField(label=_(u'Käytä salausta'), required=False)

    def save(self, *args, **kwargs):
        config = dict()
        for k, v in self.cleaned_data.items():
            field = Configuration.objects.get_or_create(key=k)[0]
            field.value = v
            field.save()
            config[k] = v

        return config
        