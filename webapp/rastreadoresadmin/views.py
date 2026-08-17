import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views import View

from busadmin.models import AsignacionRastreadores
from .models import Rastreador
from .forms import RastreadorForm

logger = logging.getLogger(__name__)

class RastreadoresAdminView(View, LoginRequiredMixin):

    def get(self, request: HttpRequest, serial: str = None) -> HttpResponse | JsonResponse:

        empresa_id = request.user.empresa_id

        if serial:
            rastreador = Rastreador.objects.filter(serial=serial, empresa_id=empresa_id).first()
            if not rastreador:
                return JsonResponse({"error": "Rastreador no encontrado"}, status=404)

            return JsonResponse({
                "serial": rastreador.serial,
                "modelo": rastreador.modelo,
                "imei": rastreador.imei,
                "iccid": rastreador.iccid,
                "numero_sim": rastreador.numero_sim,
                "operador_red": rastreador.operador_red.nombre,
                "operador_red_id": rastreador.operador_red_id,
            }, status=200)

        page = request.GET.get("page", 1)

        rastreadores = Rastreador.objects.filter(empresa_id=empresa_id)
        rastreadores_paginator = Paginator(rastreadores, 9)

        return render(request, "rastreadores.html", {
            "rastreadores_paginator": rastreadores_paginator.get_page(page),
            "form": RastreadorForm(),
        })

    def post(self, request: HttpRequest) -> HttpResponse:

        empresa_id = request.user.empresa_id

        form = RastreadorForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        try:
            Rastreador.objects.create(
                serial=form.cleaned_data["serial"],
                modelo=form.cleaned_data["modelo"],
                imei=form.cleaned_data["imei"],
                iccid=form.cleaned_data["iccid"],
                operador_red=form.cleaned_data["operador"],
                numero_sim=form.cleaned_data["numero"],
                empresa_id=empresa_id,
            )
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error interno del servidor"}, status=500)

        return JsonResponse({"message": "Rastreador creado exitosamente"}, status=201)

    def put(self, request: HttpRequest, serial: str = None) -> JsonResponse:

        empresa_id = request.user.empresa_id

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        form = RastreadorForm(data)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors}, status=400)

        updated = Rastreador.objects.filter(
            serial=form.cleaned_data["serial"],
            empresa_id=empresa_id,
        ).update(
            modelo=form.cleaned_data["modelo"],
            imei=form.cleaned_data["imei"],
            iccid=form.cleaned_data["iccid"],
            operador_red=form.cleaned_data["operador"],
            numero_sim=form.cleaned_data["numero"],
        )

        if not updated:
            return JsonResponse({"message": "Rastreador no encontrado"}, status=404)

        return JsonResponse({"message": "Rastreador actualizado correctamente"}, status=200)

    def delete(self, request: HttpRequest, serial: str = None) -> HttpResponse | JsonResponse:
        if not serial:
            return HttpResponse(status=400)

        empresa_id = request.user.empresa_id

        try:
            Rastreador.objects.filter(serial=serial, empresa_id=empresa_id).delete()
            return HttpResponse(status=204)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error interno del servidor"}, status=500)

class HistorialRastreadorView(View, LoginRequiredMixin):

    def get(self, request: HttpRequest, serial: str) -> HttpResponse:

        empresa_id = request.user.empresa_id

        rastreador = Rastreador.objects.filter(serial=serial, empresa_id=empresa_id).first()
        if not rastreador:
            return HttpResponse(status=404)

        fecha = request.GET.get("fecha", "").strip()

        asignaciones = (
            AsignacionRastreadores.objects
            .filter(rastreador_id=serial)
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

        return render(request, "historial_rastreador.html", {
            "rastreador": rastreador,
            "asignaciones": asignaciones,
            "fecha": fecha,
        })