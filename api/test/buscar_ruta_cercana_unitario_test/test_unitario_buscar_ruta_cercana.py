import asyncio

import pytest

from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.exceptions.puntos_muy_cercanos_excepcion import PuntosMuyCercanos
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.usecase.buscar_ruta_cercana import BuscarRutaCercana

ORIGEN = Coordenada(lat=0.0, lon=0.0)
DESTINO = Coordenada(lat=0.01, lon=0.0)


class RepositorioRutasFalso(RutasRepositorio):
    def __init__(self, rutas: list[Ruta]):
        self.rutas = rutas
        self.ultima_busqueda: BusquedaRuta | None = None

    def buscar_cercana(self, busqueda: BusquedaRuta) -> list[Ruta]:
        self.ultima_busqueda = busqueda
        return self.rutas

    def obtener_ruta_por_codigo(self, codigo: str) -> Ruta | None:
        raise NotImplementedError

    async def calcular_caminata(self, punto_origen, punto_destino):
        raise NotImplementedError

    def obtener_rutas_favoritas(self, email: str) -> list[Ruta]:
        raise NotImplementedError

    def agregar_ruta_favorita(self, usuario, ruta):
        raise NotImplementedError

    def eliminar_ruta_favorita(self, usuario, ruta):
        raise NotImplementedError


class CalculadorGeometriaFalso(CalculadorGeometria):
    def __init__(self, distancia_metros: float):
        self.distancia_metros = distancia_metros

    def proyectar_punto_en_trayecto(self, trayecto, punto):
        raise NotImplementedError

    def subtrayecto(self, trayecto, distancia_inicio, distancia_fin):
        raise NotImplementedError

    def simplificar(self, trayecto, tolerancia):
        raise NotImplementedError

    def longitud_metros(self, trayecto):
        raise NotImplementedError

    def distancia_puntos_metros(self, a: Coordenada, b: Coordenada) -> float:
        return self.distancia_metros

    def punto_intersecta_trayecto(self, punto, trayecto, buffer=0):
        raise NotImplementedError

    def punto_abordaje(self, trayecto, punto):
        raise NotImplementedError


def _ruta(codigo: str) -> Ruta:
    return Ruta(
        id=1,
        empresa_id=1,
        empresa_nombre="Empresa Test",
        distancia_km=10.0,
        recorrido=[[ORIGEN, DESTINO]],
        codigo=codigo,
        paradero_inicio_id=1,
        paradero_inicio_nombre="Inicio",
        paradero_final_id=2,
        paradero_final_nombre="Final",
    )


def _ejecutar(repositorio: RutasRepositorio, calculador: CalculadorGeometria, distancia_caminata: int = 500):
    caso_uso = BuscarRutaCercana(repositorio, calculador)
    busqueda = BusquedaRuta(origen=ORIGEN, destino=DESTINO, distancia_caminata=distancia_caminata)
    return asyncio.run(caso_uso.ejecutar(busqueda))


class TestBuscarRutaCercana:
    def test_lanza_puntos_muy_cercanos_cuando_la_distancia_es_menor_a_500_metros(self):
        repositorio = RepositorioRutasFalso([_ruta("R1")])
        calculador = CalculadorGeometriaFalso(distancia_metros=499)

        with pytest.raises(PuntosMuyCercanos):
            _ejecutar(repositorio, calculador)

    def test_no_lanza_excepcion_cuando_la_distancia_es_exactamente_500_metros(self):
        repositorio = RepositorioRutasFalso([_ruta("R1")])
        calculador = CalculadorGeometriaFalso(distancia_metros=500)

        resultado = _ejecutar(repositorio, calculador)

        assert resultado == [_ruta("R1")]

    def test_devuelve_las_rutas_encontradas_por_el_repositorio(self):
        rutas_esperadas = [_ruta("R1"), _ruta("R2")]
        repositorio = RepositorioRutasFalso(rutas_esperadas)
        calculador = CalculadorGeometriaFalso(distancia_metros=1000)

        resultado = _ejecutar(repositorio, calculador)

        assert resultado == rutas_esperadas

    def test_devuelve_lista_vacia_cuando_el_repositorio_no_encuentra_rutas(self):
        repositorio = RepositorioRutasFalso([])
        calculador = CalculadorGeometriaFalso(distancia_metros=1000)

        resultado = _ejecutar(repositorio, calculador)

        assert resultado == []

    def test_pasa_la_busqueda_correcta_al_repositorio(self):
        repositorio = RepositorioRutasFalso([])
        calculador = CalculadorGeometriaFalso(distancia_metros=1000)

        _ejecutar(repositorio, calculador, distancia_caminata=750)

        assert repositorio.ultima_busqueda == BusquedaRuta(origen=ORIGEN, destino=DESTINO, distancia_caminata=750)
