from django.urls import path
from .views import loginuser,cerrar_sesion

urlpatterns = [
    path('',loginuser,name='login'),
    path('logout/',cerrar_sesion,name='logout')
]