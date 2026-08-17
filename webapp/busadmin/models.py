from django.db import models
from django.db.models import Q
from loginuser.models import Empresa
from rutasadmin.models import Ruta
from rastreadoresadmin.models import Rastreador
from conductoresadmin.models import Conductor

class Bus(models.Model):
    numero_bus = models.IntegerField()
    placa = models.CharField(max_length=6, unique=True,primary_key=True)
    modelo = models.CharField(max_length=50,null=True,blank=True)
    modelo_anio = models.IntegerField()
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="buses"
    )

    class Meta:
        verbose_name = "Bus"
        verbose_name_plural = "Buses"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa","numero_bus"],
                name="unique_bus_numero_por_empresa"
            )
        ]
        
    def __str__(self):
        return self.placa
    
    @property
    def ruta_activa(self):
        cache = getattr(self,"_ruta_activa_cache",None)
        if cache is not None:
            ruta_asignada = cache[0] if cache else None
        else:
            ruta_asignada = (
                AsignacionRuta.objects
                .filter(
                bus=self,
                fecha_fin__isnull=True
                )
                .select_related("ruta")
                .first()
            )

        if not ruta_asignada:
            return None
        return ruta_asignada.ruta

    @property
    def rastreador_asignado(self):
        cache = getattr(self, "_rastreador_asignado_cache", None)
        if cache is not None:
            asignacion = cache[0] if cache else None
        else:
            asignacion = (
                AsignacionRastreadores.objects
                .filter(
                    bus=self,
                    fecha_fin__isnull=True
                )
                .select_related("rastreador")
                .first()
            )
        if not asignacion:
            return None
        return asignacion.rastreador

    @property
    def conductor_asignado(self):
        cache = getattr(self, "_conductor_asignado_cache", None)
        if cache is not None:
            asignacion = cache[0] if cache else None
        else:
            asignacion = (
                AsignacionConductor.objects
                .filter(
                    bus=self,
                    fecha_fin__isnull=True
                )
                .select_related("conductor")
                .first()
            )
        if not asignacion:
            return None
        return asignacion.conductor

class AsignacionRuta(models.Model):
    bus = models.ForeignKey(
        Bus,
        on_delete=models.CASCADE,
        related_name="asignaciones_ruta"
    )

    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name="asignaciones_ruta"
    )

    fecha_inicio = models.DateTimeField()

    fecha_fin = models.DateTimeField(
        null=True,
        blank=True
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bus"],
                condition=Q(fecha_fin__isnull=True),
                name="unique_bus_asignacion_activa",
            )
        ]

class AsignacionRastreadores(models.Model):

    fecha_inicio = models.DateTimeField()

    fecha_fin = models.DateTimeField(
        null=True,
        blank=True
    )

    bus = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="asignaciones_rastreadores"
    )

    rastreador = models.ForeignKey(
        Rastreador,
        on_delete=models.PROTECT,
        related_name="asignaciones_rastreadores"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bus"],
                condition=Q(fecha_fin__isnull=True),
                name="unique_bus_asignacion_rastreador_activa",
            )
        ]

class AsignacionConductor(models.Model):

    fecha_inicio = models.DateTimeField()

    fecha_fin = models.DateTimeField(
        null=True,
        blank=True
    )

    bus = models.ForeignKey(
        Bus,
        on_delete=models.PROTECT,
        related_name="asignaciones_conductor"
    )

    conductor = models.ForeignKey(
        Conductor,
        on_delete=models.PROTECT,
        related_name="asignaciones_conductor"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bus"],
                condition=Q(fecha_fin__isnull=True),
                name="unique_bus_asignacion_conductor_activa",
            ),
            models.UniqueConstraint(
                fields=["conductor"],
                condition=Q(fecha_fin__isnull=True),
                name="unique_conductor_asignacion_activa",
            ),
        ]