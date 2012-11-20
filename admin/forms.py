from django import forms
from accounts.models import UserProfile
from servo.models import *
from products.models import *

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

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

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
