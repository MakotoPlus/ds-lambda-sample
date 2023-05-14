from django import forms
from myall import models

class FormPaypay(forms.ModelForm):
    class Meta:
        model = models.PayPay
        fields = [
            #"title"
            "use_name"
            ,"value"
        ]
