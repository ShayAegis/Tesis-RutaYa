from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel


from domain.entities.coordenada import Coordenada

from domain.entities.caminata import Caminata
from domain.servicios.calculador_geometria import CalculadorGeometria

if TYPE_CHECKING:
    from domain.entities.models import BusquedaRuta

class Pierna(BaseModel):
    perfil: str
    coordenadas: list[Coordenada]
    punto_inicio: Coordenada
    punto_final: Coordenada
    distancia: int | float
    duracion: int
    peso: int | float

class BusPierna(Pierna):
    pass

class CaminandoPierna(Pierna):
    pass


class PiernaFabrica(ABC):
    @abstractmethod
    def crear_pierna(self,*args) -> Pierna:
        pass


class BusPiernaFabrica(PiernaFabrica):
    def __init__(self, calculador: CalculadorGeometria):

        self.calculador = calculador
        self.FACTOR_PESO_BUS_POR_METRO = 1000

    def _calcular_duracion(self,distancia: float) -> int:

        BUS_VELOCIDAD_PROMEDIO_MS = 6.06
        velocidad = BUS_VELOCIDAD_PROMEDIO_MS
        return int(distancia / velocidad)

    def crear_pierna(self, recorrido: list[Coordenada], busqueda: BusquedaRuta) -> Pierna:

        distancia = self.calculador.longitud_metros(recorrido)
        peso = distancia * self.FACTOR_PESO_BUS_POR_METRO
        duracion = self._calcular_duracion(distancia)

        return BusPierna(
            perfil="bus",
            coordenadas=recorrido,
            punto_inicio=recorrido[0],
            punto_final=recorrido[-1],
            distancia=round(distancia,2),
            duracion=duracion,
            peso=peso,
        )


class CaminandoPiernaFabrica(PiernaFabrica):
    def __init__(self, calculador: CalculadorGeometria):
        self.calculador = calculador

    def crear_pierna(self, caminata: Caminata):
        return CaminandoPierna(
            perfil="walking",
            coordenadas=caminata.recorrido,
            punto_inicio=caminata.recorrido[0],
            punto_final=caminata.recorrido[-1],
            distancia=caminata.distancia,
            duracion=caminata.duracion,
            peso=caminata.peso,
        )