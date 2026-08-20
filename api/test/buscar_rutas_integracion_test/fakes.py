from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.caminata import Caminata
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.repositories.repositorio_rutas import RutasRepositorio


class FakeRutasRepositorio(RutasRepositorio):
    """Repositorio en memoria para no depender de la base de datos en los tests."""

    def __init__(self, rutas: list[Ruta]):
        self._rutas = rutas

    def buscar_cercana(self, busqueda: BusquedaRuta) -> list[Ruta]:
        return self._rutas

    def obtener_ruta_por_codigo(self, codigo: str) -> Ruta | None:
        return next((ruta for ruta in self._rutas if ruta.codigo == codigo), None)

    async def calcular_caminata(self, punto_origen: Coordenada, punto_destino: Coordenada) -> Caminata:
        return Caminata(
            recorrido=[punto_origen, punto_destino],
            peso=100.0,
            duracion=60,
            distancia=100.0,
        )

    def obtener_rutas_favoritas(self, email: str) -> list[Ruta]:
        return []

    def agregar_ruta_favorita(self, usuario, ruta):
        pass

    def eliminar_ruta_favorita(self, usuario, ruta):
        pass
