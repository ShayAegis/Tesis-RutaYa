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
