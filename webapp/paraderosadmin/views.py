from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render, redirect
from django.db.models import Q, Count, OuterRef, Subquery
from django.db.models.functions import Coalesce

from loginuser.models import Empresa
from rutasadmin.models import Ruta
from .forms import CrearParadero
from .models import Paradero, EmpresaParadero


class ParaderosAdminView(View,LoginRequiredMixin):
    def get(self,request):
        empresaId = request.user.empresa.id

        cantidad_rutas_subquery = (
            Ruta.objects.filter(
                Q(paradero_inicio_id=OuterRef("paradero_id")) | Q(paradero_final_id=OuterRef("paradero_id")),
                empresa_id=empresaId,
            )
            .order_by()
            .values("empresa_id")
            .annotate(cantidad=Count("id"))
            .values("cantidad")
        )

        paraderos = (EmpresaParadero.objects.filter(empresa_id=empresaId)
                     .select_related("paradero")
                     .annotate(cantidad_rutas=Coalesce(Subquery(cantidad_rutas_subquery), 0))
                     .order_by("codigo")
                     .all()
                    )
        page = request.GET.get("page",1)
        paraderos_paginator = Paginator(paraderos,5)
        paraderos_mapa = [
            {
                "id": paradero.id,
                "nombre": paradero.paradero.nombre,
                "codigo": paradero.codigo,
                "lat": paradero.paradero.ubicacion.y,
                "lng": paradero.paradero.ubicacion.x,
                "radio": paradero.paradero.radio
            }
            for paradero in paraderos_paginator.page(page).object_list
        ]

        return render(request,"paraderos.html",{
            "paraderos_paginator": paraderos_paginator.get_page(page),
            "paraderos_mapa": paraderos_mapa
        })

class BuscarParaderosView(View,LoginRequiredMixin):
    def get(self, request:HttpRequest) -> HttpResponse:
        busqueda = request.GET.get("q","").strip()

        paraderos = (
            EmpresaParadero.objects.select_related("paradero")
            .filter(paradero__nombre__icontains=busqueda)
            .order_by("paradero__nombre")[:10].all()

            if busqueda else []
        )

        return JsonResponse({
            "paraderos": [
                {
                    "id": paradero.id,
                    "nombre": paradero.paradero.nombre,
                    "codigo": paradero.codigo,
                    "lat": paradero.paradero.ubicacion.y,
                    "lng": paradero.paradero.ubicacion.x,
                }
                for paradero in paraderos
            ]
        })

class CrearParaderoView(View,LoginRequiredMixin):
    def get(self,request: HttpRequest) -> HttpResponse:
        empresaId = request.user.empresa_id
        codigos_por_paradero = dict(
            EmpresaParadero.objects.filter(empresa_id=empresaId).values_list("paradero_id","codigo")
        )

        paraderos_existentes = [
            {
                "id": paradero.id,
                "nombre": paradero.nombre,
                "lat": paradero.ubicacion.y,
                "lng": paradero.ubicacion.x,
                "radio": paradero.radio,
                "codigo": codigos_por_paradero.get(paradero.id)
            }
            for paradero in Paradero.objects.all()
        ]

        return render(request,"crear_paradero.html",{
            "crearParaderoForm": CrearParadero(),
            "paraderos_existentes": paraderos_existentes
        })

    def post(self,request: HttpRequest) -> HttpResponse:
        empresaId = request.user.empresa_id
        form = CrearParadero(request.POST)
        if not form.is_valid():
            return render(request,"crear_paradero.html",{
                "crearParaderoForm": form
            })

        codigo = form.cleaned_data["codigo"]
        nombre = form.cleaned_data["nombre"]
        radio = form.cleaned_data["radio"]
        lat = form.cleaned_data["lat"]
        lng = form.cleaned_data["lng"]
        paradero_id = form.cleaned_data["paradero_id"]

        if paradero_id:
            paradero = Paradero.objects.get(id=paradero_id)
        else:
            paradero = Paradero.objects.create(
                nombre=nombre,
                ubicacion=Point(lng, lat, srid=4326),
                radio=radio
            )

        EmpresaParadero.objects.create(
            empresa_id=empresaId,
            paradero=paradero,
            codigo=codigo
        )

        return redirect("paraderosAdmin")
