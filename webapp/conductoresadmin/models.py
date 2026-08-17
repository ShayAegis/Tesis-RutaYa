from django.db import models


class Conductor(models.Model):
    cedula = models.IntegerField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
