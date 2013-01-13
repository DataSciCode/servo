#coding utf-8

from django import forms
from django.utils.translation import ugettext as _

from servo.models.account import User, UserProfile

class BasicProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)

class ProfileForm(BasicProfileForm):
    password = forms.CharField(widget=forms.PasswordInput, 
        required=False,
        label=_(u'salasana'))
    confirmation = forms.CharField(widget=forms.PasswordInput, 
        required=False,
        label=_(u'vahvistus'))

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password',)
