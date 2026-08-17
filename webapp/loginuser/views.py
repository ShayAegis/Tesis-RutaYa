from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth import authenticate,login
from .forms import LoginForm
def loginuser(request:HttpRequest):

    if request.method == 'POST':
        requestBody = request.POST
        email = requestBody.get("correo")
        contrasena = requestBody.get("contrasena")
        user = authenticate(request,username=email,password=contrasena)
        if user is not None:
            login(request, user)
            return redirect("busAdmin")
        else:

            print("no se pudo autenticar")
            
    return render(request,"login.html",{
        "loginForm": LoginForm()
    })