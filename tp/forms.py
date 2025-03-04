from http import client
from django.db.models import fields
from django import forms
from .models import product


class productform(forms.ModelForm):
    class Meta:
        model = product
        fields = '__all__'
