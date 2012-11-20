#coding=utf-8

from django import forms
from orders.models import *

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        exclude = ['created_at', 'paid_at', 'created_by', 'customer', 'order']

class SidebarForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'queue', 'status', 'priority']

class FieldsForm(forms.Form):
    pass

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = ServiceOrderItem
        fields = ['title', 'price', 'reported', 'sn']

class PartForm(forms.Form):
    partNumber = forms.CharField(max_length=18)
    comptiaCode = forms.CharField(max_length=3)
    comptiaModifier = forms.CharField(max_length=1)

class CustomerForm(forms.Form):
    firstName = forms.CharField(max_length=100)
    lastName = forms.CharField(max_length=100)
    emailAddress = forms.CharField(max_length=100)
    primaryPhone = forms.CharField(max_length=100)
    addressLine1 = forms.CharField(max_length=100)
    zipCode = forms.CharField(max_length=8)
    city = forms.CharField(max_length=32)
