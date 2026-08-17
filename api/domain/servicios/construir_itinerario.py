import polyline

from domain.entities.itinerario import Itinerario
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.ruta import Ruta
from domain.servicios.recortador_geometria import RecortadorGeometria
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.entities.pierna import BusPiernaFabrica, CaminandoPiernaFabrica, Pierna


class ConstruirItinerarioServicio:

    def __init__(self, repositorio: RutasRepositorio, calculador: CalculadorGeometria):
        self.repositorio = repositorio
        self.calculador = calculador

    async def construir(self, ruta: Ruta, busqueda: BusquedaRuta) -> tuple[Itinerario, bool]:

        recortador_geometria = RecortadorGeometria(ruta,self.calculador)
        fabrica_pierna_bus = BusPiernaFabrica(self.calculador)
        fabrica_pierna_caminando = CaminandoPiernaFabrica(self.calculador)
        geometria_recortada = recortador_geometria.recortar(busqueda.origen,busqueda.destino,busqueda.distancia_caminata)

        piernas: list[Pierna] = []

        pierna_bus = fabrica_pierna_bus.crear_pierna(geometria_recortada.recorrido,busqueda)

        if self.calculador.distancia_puntos_metros(busqueda.origen,pierna_bus.punto_inicio) >= 100:
            caminata_origen_bus = await self.repositorio.calcular_caminata(busqueda.origen,pierna_bus.punto_inicio)
            if caminata_origen_bus is not None:
                pierna_origen_bus = fabrica_pierna_caminando.crear_pierna(caminata_origen_bus)
                piernas.append(pierna_origen_bus)

        piernas.append(pierna_bus)

        if self.calculador.distancia_puntos_metros(pierna_bus.punto_final,busqueda.destino) >= 100:
            caminata_bus_destino = await self.repositorio.calcular_caminata(pierna_bus.punto_final,busqueda.destino)
            if caminata_bus_destino is not None:
                pierna_bus_destino = fabrica_pierna_caminando.crear_pierna(caminata_bus_destino)
                piernas.append(pierna_bus_destino)

        return Itinerario(piernas), geometria_recortada.retorno