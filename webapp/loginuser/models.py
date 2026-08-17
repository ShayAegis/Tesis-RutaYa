from django.db import models
from django.contrib.auth.models import AbstractUser

class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
class Usuario(AbstractUser):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )