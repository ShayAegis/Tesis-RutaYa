import json
import logging
from redis import Redis
import httpx
from typing import Any, cast

from domain.entities.models import Coordenada, SugerenciaLugar
from infrastructure.configuracion import configuracion
from domain.repositories.repositorio_lugares import RepositorioLugares

from infrastructure.models.places_suggestions import PlacesAPIResponse
from infrastructure.models.places_id_search import PlacesIDSearchResponse


logger = logging.getLogger(__name__)

TIMEOUT_SEGUNDOS = 5.0
CACHE_TTL_SEGUNDOS = 4 * 7 * 3600


class RepositorioLugaresAPIGoogle(RepositorioLugares):
    def __init__(self,redis: Redis):
        self.redis = redis
    async def autocompletar_lugar(self,entrada:str,restriccion_circulo_centro: Coordenada,
                                  restriccion_circulo_radio: int) -> PlacesAPIResponse | None:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as cliente:
                api_solicitud = await cliente.post("https://places.googleapis.com/v1/places:autocomplete",
                json={
                    "input": entrada,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": restriccion_circulo_centro.lat,
                                "longitude": restriccion_circulo_centro.lon
                            },
                            "radius": restriccion_circulo_radio
                        }
                    }
                },headers={
                    "X-Goog-Api-Key":configuracion.places_api_key,
                })
            if api_solicitud.status_code == 200:
                return PlacesAPIResponse(**api_solicitud.json())
            else:
                logger.warning("Autocompletado de lugares falló (%s): %s",
                                api_solicitud.status_code, api_solicitud.text)
                return None
        except Exception:
            logger.exception("Error al autocompletar lugar")
            return None

    async def obtener_ubicacion_de_lugar_por_id(self,id:str) -> Coordenada | None:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SEGUNDOS) as cliente:
                api_solicitud = await cliente.get(f"https://places.googleapis.com/v1/places/{id}",
                                             headers={
                                                 "X-Goog-Api-Key":configuracion.places_api_key,
                                                 "X-Goog-FieldMask":"id,location"
                                             })
            if api_solicitud.status_code == 200:
                api_respuesta = PlacesIDSearchResponse(**api_solicitud.json())
                return Coordenada(lat=api_respuesta.location.latitude,lon=api_respuesta.location.longitude)
            else:
                logger.warning("Obtener ubicación de lugar falló (%s): %s",
                                api_solicitud.status_code, api_solicitud.text)
                return None
        except Exception:
            logger.exception("Error al obtener ubicación de lugar")
            return None
    def guardar_lugar_en_cache(self,nombre_lista: str,lugar:SugerenciaLugar):

        lugar_dict: dict[str,Any] = lugar.model_dump()
        lugar_dict.pop("coincidencia_hasta_indice")
        self.redis.hset(nombre_lista, lugar.id, json.dumps(lugar_dict))
        self.redis.hexpire(nombre_lista, CACHE_TTL_SEGUNDOS,lugar.id)

    def obtener_lugar_desde_cache(self, nombre_lista: str, id: str) -> Coordenada | None:
        lugar_raw = cast(str | None, self.redis.hget(nombre_lista, id))

        if not lugar_raw:
            return None

        lugar: dict[str, Any] = json.loads(lugar_raw)
        return Coordenada(
            lat=lugar["ubicacion"]["lat"],
            lon=lugar["ubicacion"]["lon"]
        )