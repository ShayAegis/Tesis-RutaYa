from django.db import models

from loginuser.models import Empresa


class OperadorRedMovil(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "OperadorRedMovil"
        verbose_name_plural = "OperadoresRedMovil"
class Rastreador(models.Model):

    serial = models.CharField(
        primary_key=True,
        max_length=50
    )

    modelo = models.CharField(
        max_length=100
    )

    imei = models.CharField(
        max_length=15,
        unique=True
    )

    iccid = models.CharField(
        max_length=22,
        unique=True
    )

    numero_sim = models.CharField(
        max_length=15,
        unique=True
    )

    operador_red = models.ForeignKey(
        OperadorRedMovil,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rastreadores'
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='rastreadores'
    )

