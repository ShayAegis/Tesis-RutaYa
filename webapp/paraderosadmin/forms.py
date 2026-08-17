from django import forms


class CrearParadero(forms.Form):

    codigo = forms.CharField(
        label="CODIGO",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese codigo del paradero',
            'class': 'form-control'
        })
    )

    nombre = forms.CharField(
        label="NOMBRE",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese nombre del paradero',
            'class': 'form-control'
        })
    )

    radio = forms.FloatField(
        label="RADIO DE COBERTURA (metros)",
        widget=forms.NumberInput(attrs={
            'placeholder': 'Ingrese radio de cobertura',
            'class': 'form-control'
        })
    )

    lat = forms.FloatField(
        widget=forms.HiddenInput(),
        error_messages={'required': 'Seleccione la ubicación del paradero en el mapa'}
    )

    lng = forms.FloatField(
        widget=forms.HiddenInput(),
        error_messages={'required': 'Seleccione la ubicación del paradero en el mapa'}
    )

    paradero_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
