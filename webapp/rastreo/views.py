from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from busadmin.models import Bus
from loginuser.models import Usuario
from .tracking import ultimas_ubicaciones_hoy


class RastreoView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        empresa_id = cast(Usuario, request.user).empresa_id

        numeros_buses = Bus.objects.filter(empresa_id=empresa_id).values_list("numero_bus", flat=True)
        ubicaciones = ultimas_ubicaciones_hoy(numeros_buses)

        return render(request, "rastreo.html", {
            "buses_mapa": ubicaciones,
        })


class UbicacionesActualesView(LoginRequiredMixin, View):
    """Últimas ubicaciones reportadas hoy, en JSON, para refrescar el mapa por polling."""

    def get(self, request: HttpRequest) -> HttpResponse:
        empresa_id = cast(Usuario, request.user).empresa_id

        numeros_buses = Bus.objects.filter(empresa_id=empresa_id).values_list("numero_bus", flat=True)
        ubicaciones = ultimas_ubicaciones_hoy(numeros_buses)

        return JsonResponse({"buses_mapa": ubicaciones})
