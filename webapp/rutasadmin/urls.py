from django.urls import path
from .views import RutasAdminView, CrearRutaView
urlpatterns = [
    path("", RutasAdminView.as_view(), name="rutasAdmin"),
    path("<int:idRuta>",RutasAdminView.as_view(), name="rutasAdmin_id"),
    path("crear/", CrearRutaView.as_view(),name="crearRutas"),
    path("crear/<int:idRuta>", CrearRutaView.as_view(), name="crearRutas_update"),
]