from django.db import models
from busadmin.models import Empresa
from paraderosadmin.models import Paradero
from django.contrib.gis.db import models

class Ruta(models.Model):
    codigo = models.CharField(max_length=100, unique=True)

    paradero_inicio = models.ForeignKey(
        Paradero,
        on_delete=models.CASCADE,
        related_name="rutas_inicio",
    )

    paradero_final = models.ForeignKey(
        Paradero,
        on_delete=models.CASCADE,
        related_name="rutas_final"
    )

    recorrido = models.MultiLineStringField(srid=4326)

    distancia_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default = 0.0,
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="rutas"
    )

    def __str__(self):
        return "{} - {}".format(self.paradero_inicio.nombre, self.paradero_final.nombre)


class HorarioOperacion(models.Model):

    class Dia(models.IntegerChoices):
        LUNES = 0, "LUN"
        MARTES = 1, "MAR"
        MIERCOLES = 2, "MIE"
        JUEVES = 3, "JUE"
        VIERNES = 4, "VIE"
        SABADO = 5, "SAB"
        DOMINGO = 6, "DOM"

    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name="horarios",
    )

    dia = models.IntegerField(choices=Dia.choices)

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["ruta", "dia"], name="unique_dia_por_ruta")
        ]
        ordering = ["dia"]

    def __str__(self):
        return "{} - {}".format(self.ruta.codigo, self.get_dia_display())
