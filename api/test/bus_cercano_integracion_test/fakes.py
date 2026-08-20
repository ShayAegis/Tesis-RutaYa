from domain.entities.bus import Bus
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.caminata import Caminata
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_rutas import RutasRepositorio


class FakeRepositorioBuses(RepositorioBuses):
    """Repositorio en memoria para no depender de MongoDB en los tests.

    El caso de uso consulta el repositorio dos veces por ejecución: una con el
    `vuelta` solicitado (segmento solicitado) y otra con su negación (segmento
    opuesto). `buses_por_vuelta` permite simular buses que solo existen en uno
    de los dos segmentos.
    """

    def __init__(self, buses_por_vuelta: dict[bool, list[Bus]], velocidad_promedio_kmh: float | None = None):
        self._buses_por_vuelta = buses_por_vuelta
        self._velocidad_promedio_kmh = velocidad_promedio_kmh

    async def obtener_bus_cercano_por_ruta(self, lat: float, lon: float, ruta_id: str, vuelta: bool) -> list[Bus]:
        return self._buses_por_vuelta.get(vuelta, [])

    async def obtener_velocidad_promedio_diaria(self, empresa_id: int, numero_bus: int) -> float | None:
        return self._velocidad_promedio_kmh


class FakeRutasRepositorio(RutasRepositorio):
    """Repositorio en memoria para no depender de la base de datos en los tests."""

    def __init__(self, ruta: Ruta | None):
        self._ruta = ruta

    def buscar_cercana(self, busqueda: BusquedaRuta) -> list[Ruta]:
        raise NotImplementedError

    def obtener_ruta_por_codigo(self, codigo: str) -> Ruta | None:
        if self._ruta is not None and self._ruta.codigo == codigo:
            return self._ruta
        return None

    async def calcular_caminata(self, punto_origen: Coordenada, punto_destino: Coordenada) -> Caminata:
        raise NotImplementedError

    def obtener_rutas_favoritas(self, email: str) -> list[Ruta]:
        raise NotImplementedError

    def agregar_ruta_favorita(self, usuario, ruta):
        raise NotImplementedError

    def eliminar_ruta_favorita(self, usuario, ruta):
        raise NotImplementedError
