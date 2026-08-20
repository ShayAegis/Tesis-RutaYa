from abc import ABC, abstractmethod

from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_geometria import CalculadorGeometria

#Tolerancia GPS para considerar que un bus está sobre el trayecto, en grados (~35 metros)
BUFFER_INTERSECCION_TRAYECTO = 0.00035


class FiltroBuses:
    def __init__(self, ubicacion_usuario: Coordenada, calculador: CalculadorGeometria):
        self.ubicacion_usuario = ubicacion_usuario
        self.calculador_geometria = calculador

    def filtrar(self, buses: list[Bus],segmento_ruta: list[Coordenada]) -> list[Bus]:
        buses_validos = []
        for bus in buses:
            if bus.ultima_ubicacion is None:
                continue
            if not self.calculador_geometria.punto_intersecta_trayecto(bus.ultima_ubicacion, segmento_ruta, BUFFER_INTERSECCION_TRAYECTO):
                continue
            buses_validos.append(bus)
        return buses_validos

class FiltroBusesEnSegmentoSolicitado(FiltroBuses):
    def filtrar(self, buses: list[Bus],segmento_ruta: list[Coordenada]) -> list[Bus]:
        buses = super().filtrar(buses,segmento_ruta)
        proyeccion_ubicacion_usuario = self.calculador_geometria.proyectar_punto_en_trayecto(segmento_ruta, self.ubicacion_usuario)
        buses_validos = []
        for bus in buses:
            proyeccion_ubicacion_bus = self.calculador_geometria.proyectar_punto_en_trayecto(segmento_ruta, bus.ultima_ubicacion)
            if proyeccion_ubicacion_bus >= proyeccion_ubicacion_usuario:
                continue
            buses_validos.append(bus)
        return buses_validos

class FiltroBusesYaPasaronEnSegmentoSolicitado(FiltroBuses):
    def filtrar(self, buses: list[Bus],segmento_ruta: list[Coordenada]) -> list[Bus]:
        buses = super().filtrar(buses,segmento_ruta)
        proyeccion_ubicacion_usuario = self.calculador_geometria.proyectar_punto_en_trayecto(segmento_ruta, self.ubicacion_usuario)
        buses_validos = []
        for bus in buses:
            proyeccion_ubicacion_bus = self.calculador_geometria.proyectar_punto_en_trayecto(segmento_ruta, bus.ultima_ubicacion)
            if proyeccion_ubicacion_bus < proyeccion_ubicacion_usuario:
                continue
            buses_validos.append(bus)
        return buses_validos


class FiltroBusesEnSegmentoOpuesto(FiltroBuses):
    def filtrar(self, buses: list[Bus],segmento_ruta: list[Coordenada]) -> list[Bus]:
        buses_validos = super().filtrar(buses,segmento_ruta)
        return buses_validos


class CriterioOrdenamiento(ABC):
    @abstractmethod
    def ordenar(self, buses: list[Bus], segmento: list[Coordenada]) -> list[Bus]:
        pass

class OrdenarPorCercaniaAlUsuario(CriterioOrdenamiento):
    def __init__(self, ubicacion_usuario: Coordenada, calculador: CalculadorGeometria):
        self.ubicacion_usuario = ubicacion_usuario
        self.calculador = calculador

    def ordenar(self, buses: list[Bus], segmento: list[Coordenada]) -> list[Bus]:
        proyeccion_usuario = self.calculador.proyectar_punto_en_trayecto(segmento, self.ubicacion_usuario)
        return sorted(
            buses,
            key=lambda bus: proyeccion_usuario - self.calculador.proyectar_punto_en_trayecto(segmento, bus.ultima_ubicacion),
        )

class OrdenarPorCercaniaAlFinalDeSegmento(CriterioOrdenamiento):
    def __init__(self, calculador: CalculadorGeometria):
        self.calculador = calculador

    def ordenar(self, buses: list[Bus], segmento: list[Coordenada]) -> list[Bus]:
        longitud_segmento = self.calculador.longitud_metros(segmento)
        return sorted(
            buses,
            key=lambda bus: longitud_segmento - self.calculador.proyectar_punto_en_trayecto(segmento, bus.ultima_ubicacion),
        )


class SelectorBusesConFallback:
    def __init__(self, pasos: list[tuple[FiltroBuses, CriterioOrdenamiento, list[Bus], list[Coordenada]]]):
        self.pasos = pasos

    def seleccionar(self) -> list[Bus]:
        for filtro, criterio_orden, buses, segmento in self.pasos:
            candidatos = filtro.filtrar(buses, segmento)
            if candidatos:
                return criterio_orden.ordenar(candidatos, segmento)
        return []


class BuscarBusCercanoPorRuta:
    def __init__(self, repositorio_buses:RepositorioBuses,
                 repositorio_rutas: RutasRepositorio,
                 calculador: CalculadorGeometria):

        self.repositorio_buses = repositorio_buses
        self.repositorio_rutas = repositorio_rutas
        self.calculador = calculador

    async def ejecutar(self, lat:float, lon:float, ruta_id:str,vuelta:bool) -> tuple[Bus, Ruta] | None:

        ruta = self.repositorio_rutas.obtener_ruta_por_codigo(ruta_id)

        if ruta is None:
            return None

        ubicacion_usuario = Coordenada(lat=lat, lon=lon)

        segmento_solicitado = ruta.recorrido[1] if vuelta else ruta.recorrido[0]
        segmento_opuesto = ruta.recorrido[0] if vuelta else ruta.recorrido[1]

        buses_segmento_solicitado = await self.repositorio_buses.obtener_bus_cercano_por_ruta(lat, lon, ruta_id, vuelta)
        buses_segmento_opuesto = await self.repositorio_buses.obtener_bus_cercano_por_ruta(lat, lon, ruta_id, not vuelta)

        selector = SelectorBusesConFallback([
            (
                FiltroBusesEnSegmentoSolicitado(ubicacion_usuario, self.calculador),
                OrdenarPorCercaniaAlUsuario(ubicacion_usuario, self.calculador),
                buses_segmento_solicitado,
                segmento_solicitado,
            ),
            (
                FiltroBusesEnSegmentoOpuesto(ubicacion_usuario, self.calculador),
                OrdenarPorCercaniaAlFinalDeSegmento(self.calculador),
                buses_segmento_opuesto,
                segmento_opuesto,
            ),
            (
                FiltroBusesYaPasaronEnSegmentoSolicitado(ubicacion_usuario, self.calculador),
                OrdenarPorCercaniaAlFinalDeSegmento(self.calculador),
                buses_segmento_solicitado,
                segmento_solicitado,
            ),
        ])

        buses_validos = selector.seleccionar()

        return (buses_validos[0], ruta) if len(buses_validos) > 0 else None
