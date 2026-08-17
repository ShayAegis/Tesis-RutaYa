from abc import ABC, abstractmethod

from domain.entities.models import Coordenada, SugerenciaLugar
from infrastructure.models.places_suggestions import PlacesAPIResponse


class RepositorioLugares(ABC):
    @abstractmethod
    async def autocompletar_lugar(self,entrada:str,restriccion_circulo_centro: Coordenada,
                                  restriccion_circulo_radio: int) -> PlacesAPIResponse | None:
        pass
    @abstractmethod
    async def obtener_ubicacion_de_lugar_por_id(self,id:str) -> Coordenada | None:
        pass
    @abstractmethod
    def guardar_lugar_en_cache(self,nombre_lista: str,lugar:SugerenciaLugar):
        pass
    @abstractmethod
    def obtener_lugar_desde_cache(self,nombre_lista: str, id:str) -> Coordenada | None:
        pass