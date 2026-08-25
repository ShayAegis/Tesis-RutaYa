from abc import ABC, abstractmethod

from pydantic import BaseModel

from domain.entities.models import Coordenada
from datetime import time

class EstadoOperativoRastreador(BaseModel):
    numero_bus: int
    empresa_id: int
    ruta_codigo: str
    ruta_hora_inicio: time
    ruta_hora_fin: time
    paradero_inicio: Coordenada
    paradero_final: Coordenada

class RepositorioRastreadores(ABC):
    @abstractmethod
    def obtener_estado_operativo(self, serial: str) -> EstadoOperativoRastreador | None:
        pass
