# coding=utf-8

from django import forms
from django.utils.translation import ugettext as _

from servo.models.common import *
from servo.models.account import UserProfile

class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        exclude = ('statuses', )
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

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

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['last_login', 'date_joined', 'user_permissions']

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
    pct_margin = forms.DecimalField(max_digits=4, label=_('Kate %'),
        help_text=_(u'Default margin for new products'))
    pct_vat = forms.DecimalField(max_digits=4, label=_('ALV %'),
        help_text=_(u'Default VAT for new products'))
    shipping_cost = forms.DecimalField(max_digits=4, label=_('Shipping Cost'),
        help_text=_(u'Default shipping cost for new products'))

    logo = forms.FileField(label=_('Logo'), required=False)

    mail_from = forms.CharField(max_length=128, label=_('Osoite'),
        required=False)
    imap_host = forms.CharField(max_length=128, label=_('Palvelin'),
        required=False)
    imap_user = forms.CharField(max_length=128, label=_('Tunnus'),
        required=False)
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
        required=False, initial='http://example.com:13013/cgi-bin/sendsms',
        help_text=_(u'Kannel-palvelimen osoite'))
    sms_user = forms.CharField(max_length=128, label=_(u'Tunnus'), 
        required=False)
    sms_password = forms.CharField(max_length=128, label=_('Salasana'),
        widget=forms.PasswordInput, required=False)
    sms_ssl = forms.BooleanField(label=_(u'Käytä salausta'), required=False)

    def save(self, *args, **kwargs):
        config = dict()
        for k, v in self.cleaned_data.items():
            field = Configuration.objects.get_or_create(key=k)[0]
            field.value = v
            field.save()
            config[k] = v

        return config
