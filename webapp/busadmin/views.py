import json
import logging
#Typing imports
from typing import cast

#Django imports
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import IntegrityError, transaction
from django.db.models import Prefetch, Q
from django.utils import timezone
from django.utils.dateparse import parse_date

#App imports
from .models import Bus, AsignacionRuta, AsignacionRastreadores
from .forms import AddBusForm
from .exceptions import BusYaExiste
from .tracking import getLastLocation, getIconBySignal
from loginuser.models import Usuario
from rastreo.tracking import historial_ubicaciones_dia

logger = logging.getLogger(__name__)


class EmpresaScopedView(LoginRequiredMixin, View):

    def _get_empresa_id(self, request: HttpRequest) -> int:
        return cast(Usuario, request.user).empresa_id


class BusDetalleView(EmpresaScopedView):
    """Obtener o eliminar un bus puntual a partir de su placa."""

    def get(self, request: HttpRequest, placa: str) -> HttpResponse:

        empresa_id = self._get_empresa_id(request)

        bus = Bus.objects.filter(
            placa=placa,
            empresa_id=empresa_id
        ).first()

        if bus is None:
            return JsonResponse(
                {"error": "Bus no encontrado"},
                status=404
            )

        ruta_asignada = bus.asignaciones_ruta.filter(
            fecha_fin__isnull=True
        ).first()

        rastreador_asignado = bus.asignaciones_rastreadores.filter(
            fecha_fin__isnull=True
        ).first()

        return JsonResponse({
            "numero_bus": bus.numero_bus,
            "placa": bus.placa,
            "modelo": bus.modelo,
            "modelo_anio": bus.modelo_anio,
            "ruta": ruta_asignada.ruta_id if ruta_asignada else None,
            "rastreador": rastreador_asignado.rastreador_id if rastreador_asignado else None,
        })

    def delete(self, request: HttpRequest, placa: str) -> HttpResponse:
        empresa_id = self._get_empresa_id(request)
        Bus.objects.filter(placa=placa, empresa_id=empresa_id).delete()
        return HttpResponse(status=204)


class BusAdminView(EmpresaScopedView):

    def get(self, request: HttpRequest) -> HttpResponse:

        empresa_id = self._get_empresa_id(request)

        placa_search = request.GET.get("placa", "").strip()
        page = request.GET.get("page", 1)

        buses_qs = Bus.objects.filter(empresa_id=empresa_id)

        if placa_search:
            buses_qs = buses_qs.filter(placa__icontains=placa_search)

        buses = buses_qs.prefetch_related(
            Prefetch(
                "asignaciones_ruta",
                queryset=AsignacionRuta.objects.filter(
                    fecha_fin__isnull=True
                ).select_related("ruta"),
                to_attr="_ruta_activa_cache",
            ),
            Prefetch(
                "asignaciones_rastreadores",
                queryset=AsignacionRastreadores.objects.filter(
                    fecha_fin__isnull=True
                ).select_related("rastreador"),
                to_attr="_rastreador_asignado_cache",
            ),
        ).order_by('numero_bus')

        buses_paginator = Paginator(buses,10)
        buses_page = buses_paginator.get_page(page)

        buses_con_rastreador = [
            bus.placa for bus in buses_page.object_list if bus.rastreador_asignado
        ]
        ubicaciones = getLastLocation(buses_con_rastreador)

        for bus in buses_page.object_list:
            rssi = ubicaciones.get(bus.placa)
            bus.rastreador_activo = rssi is not None
            bus.signalIcon = getIconBySignal(rssi)

        return render(request, "bus.html", {
            "buses_paginator": buses_page,
            "addBusForm": AddBusForm(),
            "placa_search": placa_search
        })
    
    def post(self, request:HttpRequest) -> HttpResponse:
        
        empresa_id = self._get_empresa_id(request)

        form = AddBusForm(request.POST)

        if not form.is_valid():
            return JsonResponse({"error":form.errors},status=400)

        numero_bus = form.cleaned_data["numero_bus"]
        placa = form.cleaned_data["placa"]
        ruta_id: int = cast(int,getattr(form.cleaned_data["ruta"], "id", None))
        rastreador_id = getattr(form.cleaned_data["rastreador"], "pk", None)
        modelo = form.cleaned_data["modelo"]
        modelo_anio = form.cleaned_data["modelo_anio"]

        try:
            self._create_bus(numero_bus, placa, ruta_id, rastreador_id, modelo, modelo_anio, empresa_id)
            return JsonResponse({"message":"Bus creado exitosamente"},status=201)
        except BusYaExiste as error:
            return JsonResponse({"message":str(error)},status=409)
        except Exception as error:
            logger.exception(error)
            return JsonResponse({"message":"Error interno el servidor"},status=500)

    def put(self,request:HttpRequest):
        empresa_id = self._get_empresa_id(request)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "JSON inválido"},
                status=400
            )
        form = AddBusForm(data)

        if not form.is_valid():
            return JsonResponse({"errors":form.errors},status=400)

        numero_bus = form.cleaned_data["numero_bus"]
        placa = form.cleaned_data["placa"]
        ruta_id: int = cast(int,getattr(form.cleaned_data["ruta"], "id", None))
        rastreador_id = getattr(form.cleaned_data["rastreador"], "pk", None)
        modelo = form.cleaned_data["modelo"]
        modelo_anio = form.cleaned_data["modelo_anio"]

        try:
            self._update_bus(numero_bus,placa,ruta_id,rastreador_id, modelo,modelo_anio,empresa_id)
            return JsonResponse(
                {"message": "Bus actualizado correctamente"},
                status=200
            )
        except Bus.DoesNotExist:
            return JsonResponse({"message":"Bus no encontrado"},status=404)
        except BusYaExiste as error:
            return JsonResponse({"message":str(error)},status=409)

        except Exception as error:
            logger.exception(f"Error inesperado al actualizar el bus: {str(error)}")
            return JsonResponse(
                {"message": "Error interno del servidor"},
                status=500
            )
    @transaction.atomic
    def _create_bus(self, numero_bus, placa, ruta, rastreador_id, modelo,modelo_anio,empresa_id):
        try:

            bus, created = Bus.objects.get_or_create(
                numero_bus=numero_bus,
                empresa_id=empresa_id,
                defaults={
                    "placa": placa,
                    "modelo": modelo,
                    "modelo_anio": modelo_anio
                },
            )

            if not created:
                raise BusYaExiste("Ya existe un bus con ese número")

            ahora = timezone.now()

            if ruta is not None:
                AsignacionRuta.objects.create(
                    fecha_inicio=ahora,
                    bus_id=bus.placa,
                    ruta_id=ruta,
                )

            if rastreador_id is not None:
                AsignacionRastreadores.objects.create(
                    fecha_inicio=ahora,
                    bus_id=bus.placa,
                    rastreador_id=rastreador_id,
                )

        except IntegrityError as error:
            errorMsg = str(error).lower()
            if "placa" in errorMsg:
                raise BusYaExiste("Ya existe un bus con esa placa")
            raise BusYaExiste("No se pudo registrar el bus por un conflicto de datos")

    @transaction.atomic
    def _update_bus(self, numero_bus, placa, ruta, rastreador_id, modelo,modelo_anio, empresa_id):

        if Bus.objects.filter(
                placa=placa,
                empresa_id=empresa_id
        ).exclude(numero_bus=numero_bus).exists():
            raise BusYaExiste(
                "La placa ingresada ya está registrada en otro vehículo."
            )


        bus = Bus.objects.select_for_update().get(
            numero_bus=numero_bus,
            empresa_id=empresa_id
        )

        ahora = timezone.now()

        ruta_activa = AsignacionRuta.objects.filter(
            bus=bus,
            fecha_fin__isnull=True
        ).first()

        ruta_actual_id = ruta_activa.ruta_id if ruta_activa else None

        if ruta_actual_id != ruta:
            if ruta_activa:
                ruta_activa.fecha_fin = ahora
                ruta_activa.save(update_fields=["fecha_fin"])

            if ruta is not None:
                AsignacionRuta.objects.create(
                    bus=bus,
                    ruta_id=ruta,
                    fecha_inicio=ahora
                )

        rastreador_asignado = AsignacionRastreadores.objects.filter(
            bus=bus,
            fecha_fin__isnull=True
        ).first()

        rastreador_actual_id = rastreador_asignado.rastreador_id if rastreador_asignado else None

        if rastreador_actual_id != rastreador_id:
            if rastreador_asignado:
                rastreador_asignado.fecha_fin = ahora
                rastreador_asignado.save(update_fields=["fecha_fin"])

            if rastreador_id is not None:
                AsignacionRastreadores.objects.create(
                    bus=bus,
                    rastreador_id=rastreador_id,
                    fecha_inicio=ahora
                )

        Bus.objects.filter(pk=bus.pk).update(
            placa=placa,
            modelo=modelo,
            modelo_anio=modelo_anio
        )

class HistorialRutaBusView(EmpresaScopedView):

    def get(self, request: HttpRequest, placa: str) -> HttpResponse:

        empresa_id = self._get_empresa_id(request)

        bus = Bus.objects.filter(placa=placa, empresa_id=empresa_id).first()
        if bus is None:
            return HttpResponse(status=404)

        fecha = request.GET.get("fecha", "").strip()

        asignaciones = (
            AsignacionRuta.objects
            .filter(bus_id=placa)
            .select_related("ruta")
            .order_by("-fecha_inicio")
        )

        fecha_valida = parse_date(fecha) if fecha else None

        ubicaciones = []

        if fecha_valida:
            asignaciones = asignaciones.filter(
                fecha_inicio__date__lte=fecha_valida
            ).filter(
                Q(fecha_fin__isnull=True) | Q(fecha_fin__date__gte=fecha_valida)
            )
            ubicaciones = historial_ubicaciones_dia(placa, fecha_valida)

        return render(request, "historial_ruta_bus.html", {
            "bus": bus,
            "asignaciones": asignaciones,
            "fecha": fecha,
            "mostrar_mapa": fecha_valida is not None,
            "ubicaciones": ubicaciones,
        })