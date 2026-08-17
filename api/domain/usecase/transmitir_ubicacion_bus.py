import json
from typing import AsyncIterator

from application.dto.buses_dto import ActualizacionUbicacionDTO
from domain.repositories.repositorio_transmision_ubicacion_bus import RepositorioTransmisionUbicacionBus
from infrastructure.configuracion import configuracion

CAMPOS_UBICACION = ("lat", "lon", "velocidad", "azimut", "timestamp")


class TransmitirUbicacionBus:
    def __init__(self, repositorio: RepositorioTransmisionUbicacionBus):
        self.repositorio = repositorio

    async def ejecutar(self, empresa_id: int, ruta_id: str, numero_bus: int) -> AsyncIterator[ActualizacionUbicacionDTO]:
        tema = f"{configuracion.mqtt_basetopic}/{empresa_id}/{ruta_id}/{numero_bus}"
        async for mensaje in self.repositorio.suscribir(tema):
            datos = json.loads(mensaje)
            ubicacion = {campo: datos[campo] for campo in CAMPOS_UBICACION}
            yield ActualizacionUbicacionDTO(**ubicacion)
