from http import client
from django.db.models import fields
from django import forms
from .models import SellProduct


class productform(forms.ModelForm):
    class Meta:
        model = SellProduct
        fields = '__all__'
