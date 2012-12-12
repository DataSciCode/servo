#coding=utf-8

from django import forms
from orders.models import *
from products.models import *

class LocalizedModelForm(forms.ModelForm):
    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelForm, cls).__new__(cls, *args, **kwargs)
        for field in new_class.base_fields.values():
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True

        return new_class

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder

class PurchaseOrderItemForm(LocalizedModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ('sn', 'amount')

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('files')
