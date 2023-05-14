from django import forms
from myall import models

class FormLine(forms.ModelForm):
    class Meta:
        model = models.LinePay
        fields = [
            'use_name'
            ,'value'
            ,'lineid'
        ]
