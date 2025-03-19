from http import client
from django.db.models import fields
from django import forms
from .models import Product


class productform(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
