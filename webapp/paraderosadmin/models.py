from django.contrib.gis.db import models

from loginuser.models import Empresa

class Paradero(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.PointField(srid=4326)
    radio = models.FloatField()
    def __str__(self):
        return self.nombre


class EmpresaParadero(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="paraderos"
    )
    paradero = models.ForeignKey(
        Paradero,
        on_delete=models.CASCADE,
        related_name="empresas"
     )

    codigo = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "paradero"],
                name="unique_paradero_empresa",
            ),
            models.UniqueConstraint(
                fields=["empresa", "codigo"],
                name="unique_codigo_paradero_empresa"
            )
        ]