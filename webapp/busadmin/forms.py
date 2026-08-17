from typing import cast

from django import forms
from django.db.models import Exists, OuterRef

from .models import Ruta, AsignacionRastreadores
from rastreadoresadmin.models import Rastreador

class RutaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.codigo

class RastreadorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.serial

class AddBusForm(forms.Form):

    numero_bus = forms.IntegerField(
        label="NÚMERO DE UNIDAD",
        widget=forms.NumberInput(attrs={
            "placeholder": "Ingrese el número de la unidad",
            "autocomplete": "off",
            "class":"form-control"
        })
    )

    placa = forms.CharField(
        label="PLACA",
        max_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "Ingrese la placa de la unidad",
            "autocomplete": "off",
            "class":"form-control"
        })
    )
    modelo = forms.CharField(
        label="MODELO",
        widget=forms.TextInput(attrs={
            "placeholder": "Ingrese el modelo",
            "class":"form-control"
        }),
        required=True
    )

    modelo_anio = forms.IntegerField(
        label="AÑO MODELO",
        widget=forms.NumberInput(attrs={
            "placeholder": "Ingrese el año del modelo",
            "autocomplete": "off",
            "class":"form-control"
        }),
        required=True
    )
    ruta = RutaChoiceField(
        label="RUTA ASIGNADA",
        queryset=Ruta.objects.all(),
        empty_label="Seleccione la ruta",
        widget=forms.Select({
            "class":"form-control"
        }),
        required=False
    )
    activar_rastreador = forms.BooleanField(
        label="Configurar Rastreador",
        widget=forms.CheckboxInput({
            "id":"activar-rastreador",
            "class":"form-check-input"
        }),
        required=False
    )

    rastreador = RastreadorChoiceField(
        label="RASTREADOR",
        queryset=Rastreador.objects.filter(
            ~Exists(
                AsignacionRastreadores.objects.filter(
                    rastreador=OuterRef("pk"),
                    fecha_fin__isnull=True,
                )
            )
        ),
        empty_label="Seleccione el rastreador",
        widget=forms.Select(attrs={
            "disabled":True,
            "id":"rastreador-input",
            "class":"form-control"
        }),
        required=False
    )

    def __init__(self,*args,user=None,**kwargs):
        super().__init__(*args,**kwargs)

        if user is not None:
            cast(forms.ModelChoiceField,self.fields["ruta"]).queryset = Ruta.objects.filter(
                empresa = user.id
            )

    def clean(self):

        cleaned_data = super().clean()

        activar_rastreador = cleaned_data["activar_rastreador"]
        rastreador = cleaned_data.get("rastreador")

        if not activar_rastreador:
            cleaned_data["rastreador"] = None

        elif not rastreador:
            self.add_error(
                "rastreador",
                "Debe seleccionar un rastreador cuando el rastreador está activado."
            )

        return cleaned_data
    def clean_placa(self):
        placa = self.cleaned_data["placa"].upper()
        return placa