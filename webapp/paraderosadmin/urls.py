from django.urls import path

from .views import ParaderosAdminView, BuscarParaderosView, CrearParaderoView

urlpatterns = [
    path("",ParaderosAdminView.as_view(),name='paraderosAdmin'),
    path("buscar/",BuscarParaderosView.as_view(),name='buscarParaderos'),
    path("crear/",CrearParaderoView.as_view(),name='crearParadero')
]