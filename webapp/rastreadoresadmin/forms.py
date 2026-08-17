from django import forms
from .models import OperadorRedMovil

class RastreadorForm(forms.Form):
    serial = forms.CharField(label="SERIAL",max_length=100,
                             widget=forms.TextInput(attrs={
                                 'class':'form-control',
                                 'autocomplete':'off'
                             }))

    modelo = forms.CharField(label="MODELO",max_length=100,
                             widget=forms.TextInput(attrs={
                                 'class':'form-control'
                             }))

    imei = forms.IntegerField(label="IMEI",widget=forms.TextInput(attrs={
        'class':'form-control',
        'autocomplete':'off',
        'maxlength':'15'
    }))

    iccid = forms.IntegerField(label="ICCID",widget=forms.TextInput(attrs={
        'class':'form-control',
        'autocomplete':'off',
        'maxlength':'20'
    }))

    numero = forms.IntegerField(label="NUMERO DE SIM",widget=forms.TextInput(attrs={
        'class':'form-control',
        'autocomplete':'off',
        'maxlength':'10'
    }))

    operador = forms.ModelChoiceField(label="OPERADOR",
                                      queryset=OperadorRedMovil.objects.all(),
                                      widget=forms.Select(attrs={
                                        'class':'form-control'
    }))