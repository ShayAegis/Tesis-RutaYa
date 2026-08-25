from django import forms
from django.contrib.gis.geos import GEOSGeometry, GEOSException
from django.forms import formset_factory

from paraderosadmin.models import Paradero
from .models import HorarioOperacion

class CrearRutas(forms.Form):

    codigo = forms.CharField(
        label="CODIGO",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese codigo de la ruta',
            'class':'form-control'
        })
    )

    punto_inicio_nombre = forms.CharField(
        label="INICIO DE RUTA",
        widget=forms.TextInput(attrs={
            'placeholder': 'Escriba el paradero de inicio',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )

    punto_inicio = forms.ModelChoiceField(
        queryset=Paradero.objects.all(),
        widget=forms.HiddenInput(),
        error_messages={'invalid_choice': 'Seleccione un paradero de inicio válido de la lista de sugerencias'}
    )

    punto_final_nombre = forms.CharField(
        label="FIN DE RUTA",
        widget=forms.TextInput(attrs={
            'placeholder': 'Escriba el paradero final',
            'class': 'form-control',
            'autocomplete': 'off',
        })
    )
    punto_final = forms.ModelChoiceField(
        queryset=Paradero.objects.all(),
        widget=forms.HiddenInput(),
        error_messages={'invalid_choice': 'Seleccione un paradero final válido de la lista de sugerencias'}
    )

    distancia = forms.FloatField(
        label="Distancia de la ruta",
        widget=forms.HiddenInput()
    )

    recorrido = forms.CharField(
        widget=forms.HiddenInput()
    )

    def clean_recorrido(self):
        raw = self.cleaned_data["recorrido"]
        try:
            geom = GEOSGeometry(raw, srid=4326)
        except (GEOSException, ValueError, TypeError):
            raise forms.ValidationError("El recorrido no es una geometría válida.")

        if geom.geom_type != "MultiLineString":
            raise forms.ValidationError(
                "El recorrido debe ser un MultiLineString con el segmento de inicio y el de fin."
            )

        return geom


DIAS_SEMANA = HorarioOperacion.Dia.choices


class HorarioOperacionForm(forms.Form):

    dia = forms.IntegerField(widget=forms.HiddenInput())

    hora_inicio = forms.TimeField(
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )

    hora_fin = forms.TimeField(
        required=False,
        input_formats=['%H:%M'],
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    )

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if bool(hora_inicio) != bool(hora_fin):
            raise forms.ValidationError("Complete ambas horas o deje el día sin marcar.")

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        return cleaned_data

    def is_activo(self):
        return bool(self.cleaned_data.get("hora_inicio") and self.cleaned_data.get("hora_fin"))


HorarioOperacionFormSet = formset_factory(HorarioOperacionForm, extra=7, max_num=7)