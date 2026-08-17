from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from domain.entities.coordenada import Coordenada
from domain.servicios.calculador_geometria import CalculadorGeometria

if TYPE_CHECKING:
    from domain.entities.models import BusquedaRuta

TOLERANCIA_SIMPLIFICACION_GRADOS = 10 / 111320


@dataclass
class ContextoProcesamientoRuta:
    geometria: list[Coordenada]
    busqueda: BusquedaRuta
    distancia_origen: Optional[float] = None
    distancia_destino: Optional[float] = None


class ManejadorProcesamientoRuta(ABC):
    def __init__(self, calculador: CalculadorGeometria):
        self.calculador = calculador
        self._siguiente: Optional["ManejadorProcesamientoRuta"] = None

    def establecer_siguiente(self, siguiente: "ManejadorProcesamientoRuta") -> "ManejadorProcesamientoRuta":
        self._siguiente = siguiente
        return siguiente

    def manejar(self, contexto: ContextoProcesamientoRuta) -> ContextoProcesamientoRuta:
        contexto = self._procesar(contexto)
        if self._siguiente is not None:
            return self._siguiente.manejar(contexto)
        return contexto

    @abstractmethod
    def _procesar(self, contexto: ContextoProcesamientoRuta) -> ContextoProcesamientoRuta:
        pass


class CortarSegmentoRuta(ManejadorProcesamientoRuta):
    def _procesar(self, contexto: ContextoProcesamientoRuta) -> ContextoProcesamientoRuta:
        geometria = contexto.geometria
        distancia_origen = self.calculador.proyectar_punto_en_trayecto(geometria, contexto.busqueda.origen)
        distancia_destino = self.calculador.proyectar_punto_en_trayecto(geometria, contexto.busqueda.destino)
        inicio, fin = sorted((distancia_origen, distancia_destino))

        subtrayecto = self.calculador.subtrayecto(geometria, inicio, fin)
        if distancia_origen > distancia_destino:
            subtrayecto = list(reversed(subtrayecto))

        contexto.geometria = subtrayecto
        contexto.distancia_origen = distancia_origen
        contexto.distancia_destino = distancia_destino
        return contexto


class SimplificarGeometriaRuta(ManejadorProcesamientoRuta):
    def _procesar(self, contexto: ContextoProcesamientoRuta) -> ContextoProcesamientoRuta:
        contexto.geometria = self.calculador.simplificar(contexto.geometria, TOLERANCIA_SIMPLIFICACION_GRADOS)
        return contexto


def crear_cadena_procesamiento_ruta(calculador: CalculadorGeometria) -> ManejadorProcesamientoRuta:
    cortar = CortarSegmentoRuta(calculador)
    simplificar = SimplificarGeometriaRuta(calculador)
    cortar.establecer_siguiente(simplificar)
    return cortar
