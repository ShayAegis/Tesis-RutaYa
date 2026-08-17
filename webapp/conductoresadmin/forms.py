from typing import cast

from django import forms
from django.db.models import Exists, OuterRef

from busadmin.models import Bus, AsignacionConductor


class BusChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.placa


class ConductorForm(forms.Form):
    cedula = forms.IntegerField(
        label="CEDULA",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )

    nombres = forms.CharField(
        label="NOMBRES",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    apellidos = forms.CharField(
        label="APELLIDOS",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    placa_bus = BusChoiceField(
        label="PLACA DEL BUS ASIGNADO",
        queryset=Bus.objects.none(),
        empty_label="Seleccione el bus que conduce",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        required=False
    )

    def __init__(self, *args, empresa_id=None, cedula=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa_id is not None:
            buses_ocupados = AsignacionConductor.objects.filter(
                bus=OuterRef("pk"),
                fecha_fin__isnull=True,
            )
            if cedula is not None:
                buses_ocupados = buses_ocupados.exclude(conductor_id=cedula)

            cast(forms.ModelChoiceField, self.fields["placa_bus"]).queryset = Bus.objects.filter(
                empresa_id=empresa_id
            ).filter(~Exists(buses_ocupados))
