from django import forms

class LoginForm(forms.Form):
    correo = forms.CharField(label="Correo Electrónico",max_length=100,required=True,widget=forms.TextInput({
        "placeholder":"Ingrese su correo electrónico",
        "class":"form-control"
    }))
    contrasena = forms.CharField(label="Contraseña",max_length=100,required=True,widget=forms.PasswordInput({
        "placeholder":"Ingrese su contraseña",
        "class":"form-control"
    })) 