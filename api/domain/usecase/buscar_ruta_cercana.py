from typing import List, Optional

from domain.entities.ruta import Ruta
from domain.entities.busqueda_ruta import BusquedaRuta

from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.exceptions.puntos_muy_cercanos_excepcion import PuntosMuyCercanos

class BuscarRutaCercana:
    def __init__(self, repositorio: RutasRepositorio, calculador: CalculadorGeometria):
        self.repositorio = repositorio
        self.calculador = calculador

    async def ejecutar(self, busqueda: BusquedaRuta) -> List[Ruta]:

        if self.calculador.distancia_puntos_metros(busqueda.origen,busqueda.destino) < 500:
            raise PuntosMuyCercanos

        rutas = self.repositorio.buscar_cercana(busqueda)
        return rutas
