from abc import ABC, abstractmethod
from inspect import walktree

from pydantic import BaseModel

from domain.entities.models import Coordenada
from domain.entities.rastreador import Rastreador
from datetime import time

class EstadoOperativoRastreador(BaseModel):
    numero_bus: int
    empresa_id: int
    placa: str
    ruta_codigo: str
    ruta_hora_inicio: time
    ruta_hora_fin: time
    paradero_inicio: Coordenada
    paradero_final: Coordenada

class RepositorioRastreadores(ABC):
    @abstractmethod
    def obtener_estado_operativo(self, serial: str) -> EstadoOperativoRastreador | None:
        pass
    @abstractmethod
    def obtener_rastreador_por_serial(self,serial:str) -> Rastreador | None:
        pass
    @abstractmethod
    def verificar_rastreador_registrado(self,serial:str) -> bool:
        pass
    @abstractmethod
    def registrar_secreto(self,serial:str,secreto_hasheado:str) -> None:
        pass
    @abstractmethod
    def obtener_hash_secreto(self,serial:str) -> str | None:
        pass
