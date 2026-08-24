#Django imports
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q ,Count

from busadmin.models import AsignacionRuta
from paraderosadmin.models import EmpresaParadero
#App imports
from .forms import CrearRutas
from .models import Ruta

class RutasAdminView(View,LoginRequiredMixin):

    def get(self, request:HttpRequest) -> HttpResponse:

        empresaId = request.user.empresa_id

        ruta_search = request.GET.get("ruta","").strip()
        page = request.GET.get("page",1)

        rutas = (
            Ruta.objects
            .filter(empresa_id=empresaId)
            .select_related("paradero_inicio","paradero_final")
            .order_by("codigo")
            .annotate(
                cantidad_buses=Count(
                    "asignaciones_ruta__bus",
                    filter=Q(asignaciones_ruta__fecha_fin__isnull=True),
                    distinct=True,
                )
            )
        )

        if ruta_search:
            rutas = rutas.filter(codigo__icontains=ruta_search)

        rutas_paginator = Paginator(rutas,5)
        rutas_mapa = [
            {
                "id": ruta.id,
                "codigo": ruta.codigo,
                "recorrido": json.loads(ruta.recorrido.geojson),
            }
            for ruta in rutas_paginator.page(page).object_list
        ]

        return render(request,"rutas.html",{
            "rutas_paginator":rutas_paginator.get_page(page),
            "ruta_search":ruta_search,
            "rutas_mapa":rutas_mapa
        })

    def delete(self, request:HttpRequest,idRuta:int) -> HttpResponse:
        idEmpresa = request.user.empresa_id

        ruta = (Ruta.objects
        .filter(empresa_id=idEmpresa,id=idRuta)
        .annotate(cantidad_buses=Count("buses"))
        .first())

        if ruta is None:
            return JsonResponse(
                {"error": "Ruta no encontrada"},
                status=404
            )

        if ruta.cantidad_buses > 0:
            return JsonResponse(
                {"error": "No se puede eliminar la ruta porque tiene buses asignados"},
                status=409
            )

        ruta.delete()

        return JsonResponse(
            {"message": "Ruta eliminada correctamente"},
            status=200
        )

class CrearRutaView(View,LoginRequiredMixin):

    def get(self,request: HttpRequest,idRuta:int|None = None) -> HttpResponse:
        if not idRuta:
            return render(request,"crear_rutas.html",{
                "crearRutaForm":CrearRutas()
            })
        empresaId = request.user.empresa_id
        ruta = Ruta.objects.get(empresa_id=empresaId,id=idRuta)
        form = CrearRutas(initial={
            "codigo":ruta.codigo,
            "punto_inicio": ruta.paradero_inicio,
            "punto_inicio_nombre": ruta.paradero_inicio.nombre,
            "punto_final": ruta.paradero_final,
            "punto_final_nombre": ruta.paradero_final.nombre,
            "distancia": ruta.distancia_km,
            "recorrido": ruta.recorrido.geojson
        })
        return render(request,"crear_rutas.html",{
            "crearRutaForm":form,
            "puntoInicioParadero":ruta.paradero_inicio,
            "puntoFinalParadero":ruta.paradero_final,
        })
    def post(self,request: HttpRequest, idRuta:int|None=None) -> HttpResponse:

        empresaId = request.user.empresa_id
        form = CrearRutas(request.POST)
        if not form.is_valid():
            return render(request,"crear_rutas.html",{
                "crearRutaForm":form
            })
        codigo = form.cleaned_data["codigo"]
        punto_inicio = form.cleaned_data["punto_inicio"]
        punto_final = form.cleaned_data["punto_final"]
        distancia = form.cleaned_data["distancia"]
        recorrido = form.cleaned_data["recorrido"]

        if not idRuta:
            paraderos_faltantes = [
                paradero.nombre
                for paradero in (punto_inicio, punto_final)
                if not EmpresaParadero.objects.filter(
                    empresa_id=empresaId, paradero_id=paradero.id
                ).exists()
            ]

            if paraderos_faltantes:
                return render(request, "crear_rutas.html", {
                    "crearRutaForm": form,
                    "paradero_faltante_error": (
                        "El paradero {} no ha sido creado para tu empresa. "
                        "Ve a Paraderos y créalo antes de continuar."
                    ).format(", ".join(paraderos_faltantes)),
                })

            Ruta.objects.create(
                codigo= codigo,
                paradero_inicio = punto_inicio,
                paradero_final = punto_final,
                distancia_km = distancia,
                recorrido = recorrido,
                empresa_id=empresaId
            )

            return redirect("crearRutas")
        if idRuta:
            Ruta.objects.filter(id=idRuta, empresa_id=empresaId).update(
                codigo=codigo,
                paradero_inicio=punto_inicio,
                paradero_final=punto_final,
                distancia_km=distancia,
                recorrido=recorrido,
            )

        return redirect("crearRutas_update",idRuta=idRuta)
