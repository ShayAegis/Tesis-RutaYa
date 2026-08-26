from django.contrib import admin
from .models import OperadorRedMovil, Rastreador

# Register your models here.

admin.site.register(OperadorRedMovil)


@admin.register(Rastreador)
class RastreadorAdmin(admin.ModelAdmin):
    list_display = ("serial", "modelo", "imei", "iccid", "numero_sim", "operador_red", "empresa")
    search_fields = ("serial", "modelo", "imei", "iccid", "numero_sim")
    list_filter = ("operador_red", "empresa")

