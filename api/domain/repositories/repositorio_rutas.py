from abc import ABC, abstractmethod

from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.entities.usuario import Usuario
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.caminata import Caminata

class RutasRepositorio(ABC):
    @abstractmethod
    def buscar_cercana(self, busqueda: BusquedaRuta) -> list[Ruta]:
        pass
    @abstractmethod
    def obtener_ruta_por_codigo(self,codigo:str) -> Ruta | None:
        pass
    @abstractmethod
    async def calcular_caminata(self, punto_origen:Coordenada, punto_destino:Coordenada) -> Caminata | None:
        pass
    @abstractmethod
    def obtener_rutas_favoritas(self,email:str) -> list[Ruta]:
        pass
    @abstractmethod
    def agregar_ruta_favorita(self,usuario:Usuario,ruta:int):
        pass
    @abstractmethod
    def eliminar_ruta_favorita(self,usuario:Usuario,ruta:int):
        pass