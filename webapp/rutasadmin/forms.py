from django import forms
from django.contrib.gis.geos import GEOSGeometry, GEOSException

from paraderosadmin.models import Paradero

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