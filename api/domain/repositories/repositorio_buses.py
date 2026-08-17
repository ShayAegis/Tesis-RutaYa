from abc import abstractmethod, ABC

from domain.entities.bus import Bus


class RepositorioBuses(ABC):
    @abstractmethod
    async def obtener_bus_cercano_por_ruta(self,lat:float,lon:float,ruta_id:str,vuelta:bool) -> list[Bus]:
        pass

    @abstractmethod
    async def obtener_velocidad_promedio_diaria(self, empresa_id: int, numero_bus: int) -> float | None:
        pass
