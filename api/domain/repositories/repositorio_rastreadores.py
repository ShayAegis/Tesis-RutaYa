from abc import ABC, abstractmethod

from pydantic import BaseModel

from domain.entities.models import Coordenada


class EstadoOperativoRastreador(BaseModel):
    numero_bus: int
    empresa_id: int
    ruta_codigo: str
    paradero_inicio: Coordenada
    paradero_final: Coordenada

class RepositorioRastreadores(ABC):
    @abstractmethod
    def obtener_estado_operativo(self, serial: str) -> EstadoOperativoRastreador | None:
        pass
