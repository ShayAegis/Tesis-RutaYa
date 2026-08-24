import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View

from busadmin.models import AsignacionConductor
from .models import Conductor
from .forms import ConductorForm

logger = logging.getLogger(__name__)

class ConductoresAdminView(View, LoginRequiredMixin):

    def get(self, request: HttpRequest, cedula: int = None) -> HttpResponse | JsonResponse:

        empresa_id = request.user.empresa_id

        if cedula:
            conductor = Conductor.objects.filter(cedula=cedula).first()
            if not conductor:
                return JsonResponse({"error": "Conductor no encontrado"}, status=404)

            asignacion_activa = conductor.asignaciones_conductor.filter(
                fecha_fin__isnull=True
            ).first()

            return JsonResponse({
                "cedula": conductor.cedula,
                "nombres": conductor.nombres,
                "apellidos": conductor.apellidos,
                "placa_bus": asignacion_activa.bus_id if asignacion_activa else None,
            }, status=200)

        page = request.GET.get("page", 1)

        bus_asignado_subquery = AsignacionConductor.objects.filter(
            conductor_id=OuterRef("cedula"),
            fecha_fin__isnull=True
        ).values("bus_id")[:1]

        conductores = Conductor.objects.annotate(
            bus_asignado=Subquery(bus_asignado_subquery)
        ).order_by("cedula")
        conductores_paginator = Paginator(conductores, 9)

        return render(request, "conductores.html", {
            "conductores_paginator": conductores_paginator.get_page(page),
            "form": ConductorForm(empresa_id=empresa_id),
        })

    def post(self, request: HttpRequest) -> HttpResponse:

        empresa_id = request.user.empresa_id

        form = ConductorForm(request.POST, empresa_id=empresa_id)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        try:
            self._crear_conductor(form.cleaned_data)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error interno del servidor"}, status=500)

        return JsonResponse({"message": "Conductor creado exitosamente"}, status=201)

    def put(self, request: HttpRequest, cedula: int = None) -> JsonResponse:

        empresa_id = request.user.empresa_id

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        form = ConductorForm(data, empresa_id=empresa_id, cedula=cedula)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        try:
            updated = self._actualizar_conductor(form.cleaned_data)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error interno del servidor"}, status=500)

        if not updated:
            return JsonResponse({"message": "Conductor no encontrado"}, status=404)

        return JsonResponse({"message": "Conductor actualizado correctamente"}, status=200)

    def delete(self, request: HttpRequest, cedula: int = None) -> HttpResponse | JsonResponse:
        if not cedula:
            return HttpResponse(status=400)

        try:
            Conductor.objects.filter(cedula=cedula).delete()
            return HttpResponse(status=204)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error interno del servidor"}, status=500)

    @transaction.atomic
    def _crear_conductor(self, cleaned_data):
        conductor = Conductor.objects.create(
            cedula=cleaned_data["cedula"],
            nombres=cleaned_data["nombres"],
            apellidos=cleaned_data["apellidos"],
        )

        bus = cleaned_data.get("placa_bus")
        if bus is not None:
            AsignacionConductor.objects.create(
                fecha_inicio=timezone.now(),
                bus=bus,
                conductor=conductor,
            )

    @transaction.atomic
    def _actualizar_conductor(self, cleaned_data):
        cedula = cleaned_data["cedula"]

        updated = Conductor.objects.filter(
            cedula=cedula,
        ).update(
            nombres=cleaned_data["nombres"],
            apellidos=cleaned_data["apellidos"],
        )

        if not updated:
            return False

        bus = cleaned_data.get("placa_bus")

        asignacion_activa = AsignacionConductor.objects.filter(
            conductor_id=cedula,
            fecha_fin__isnull=True
        ).first()

        bus_actual_id = asignacion_activa.bus_id if asignacion_activa else None
        nuevo_bus_id = bus.placa if bus else None

        if bus_actual_id != nuevo_bus_id:
            ahora = timezone.now()

            if asignacion_activa:
                asignacion_activa.fecha_fin = ahora
                asignacion_activa.save(update_fields=["fecha_fin"])

            if bus is not None:
                AsignacionConductor.objects.create(
                    fecha_inicio=ahora,
                    bus=bus,
                    conductor_id=cedula,
                )

        return True

class HistorialConductorView(View, LoginRequiredMixin):

    def get(self, request: HttpRequest, cedula: int) -> HttpResponse:

        conductor = Conductor.objects.filter(cedula=cedula).first()
        if not conductor:
            return HttpResponse(status=404)

        fecha = request.GET.get("fecha", "").strip()

        asignaciones = (
            AsignacionConductor.objects
            .filter(conductor_id=cedula)
            .select_related("bus")
            .order_by("-fecha_inicio")
        )

        fecha_valida = parse_date(fecha) if fecha else None

        if fecha_valida:
            asignaciones = asignaciones.filter(
                fecha_inicio__date__lte=fecha_valida
            ).filter(
                Q(fecha_fin__isnull=True) | Q(fecha_fin__date__gte=fecha_valida)
            )

        return render(request, "historial_conductor.html", {
            "conductor": conductor,
            "asignaciones": asignaciones,
            "fecha": fecha,
        })
