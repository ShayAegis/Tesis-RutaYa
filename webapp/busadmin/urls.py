from django.urls import path
from .views import BusAdminView, BusDetalleView, HistorialRutaBusView
urlpatterns = [
    path("", BusAdminView.as_view(), name="busAdmin"),
    path("<str:placa>/historial", HistorialRutaBusView.as_view(), name="historialRutaBus"),
    path("<str:placa>", BusDetalleView.as_view(), name="bus_admin_placa"),
]
