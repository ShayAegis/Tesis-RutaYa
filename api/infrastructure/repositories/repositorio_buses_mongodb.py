from datetime import datetime,timedelta,timezone
from typing import Mapping,Any

from motor.motor_asyncio import AsyncIOMotorCollection

from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.repositories.repositorio_buses import RepositorioBuses


class RepositorioBusesMongodb(RepositorioBuses):
    def __init__(self, mongodb:AsyncIOMotorCollection[Mapping[str,Any]]):
        self.mongodb = mongodb
    def _a_dominio(self, buses:list[dict[str,Any]]) -> list[Bus]:
        return [
            Bus(
                placa=bus['metadata']['placa'],
                numero_bus=bus['metadata']['numero_bus'],
                empresa_id=bus['metadata']['empresa_id'],
                ultima_ubicacion=Coordenada(
                    lat=bus['location']['coordinates'][1],
                    lon=bus['location']['coordinates'][0]
                )
            )
            for bus in buses
        ]

    async def obtener_bus_cercano_por_ruta(self,lat:float,lon:float,ruta_id:str,vuelta:bool) -> list[Bus]:
        marca_tiempo = datetime.now(timezone.utc) - timedelta(seconds=15)
        pipeline = [
            {"$geoNear":{"near":{"type":"Point","coordinates":[lon,lat]},
                         "distanceField":"distancia","spherical":True,
                         "key":"location"
                         }
            },
            {"$match":{
                "metadata.ruta_codigo":ruta_id,
                "timestamp":{"$gte":marca_tiempo},
                "es_vuelta": vuelta
             }},
            {"$sort":{"distancia":1,"timestamp":-1}},
            {"$group":{
                "_id":"$metadata.numero_bus",
                "posicion":{"$first":"$$ROOT"},
            }},
            {
                "$replaceWith": "$posicion"
            },
            {
                "$sort": {
                    "distancia": 1
                }
            },
        ]

        cursor = self.mongodb.aggregate(pipeline)
        resultado = await cursor.to_list(length=None)

        if not resultado:
            return []

        return self._a_dominio(resultado)

    async def obtener_velocidad_promedio_diaria(self, empresa_id: int, numero_bus: int) -> float | None:
        inicio_dia = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {
                "metadata.empresa_id": empresa_id,
                "metadata.numero_bus": numero_bus,
                "timestamp": {"$gte": inicio_dia},
            }},
            {"$group": {
                "_id": None,
                "velocidad_promedio": {"$avg": "$velocidad"},
            }},
        ]

        cursor = self.mongodb.aggregate(pipeline)
        resultado = await cursor.to_list(length=None)

        if not resultado:
            return None

        return resultado[0]["velocidad_promedio"]
