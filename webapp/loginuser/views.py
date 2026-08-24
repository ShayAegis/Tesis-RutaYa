from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate,login,logout
from .forms import LoginForm
def loginuser(request:HttpRequest):

    error = None

    if request.method == 'POST':
        requestBody = request.POST
        email = requestBody.get("correo")
        contrasena = requestBody.get("contrasena")
        user = authenticate(request,username=email,password=contrasena)
        if user is not None:
            login(request, user)
            return redirect("busAdmin")
        else:
            error = "Correo o contraseña incorrecta"

    return render(request,"login.html",{
        "loginForm": LoginForm(),
        "error": error
    })

def cerrar_sesion(request:HttpRequest):
    logout(request)
    return redirect("login")