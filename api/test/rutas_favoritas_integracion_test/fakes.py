from domain.entities.bus import Bus
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.caminata import Caminata
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_rutas import RutasRepositorio


class FakeRutasRepositorio(RutasRepositorio):
    """Repositorio en memoria para no depender de la base de datos en los tests."""

    def __init__(
        self,
        rutas_favoritas: list[Ruta] | None = None,
        ruta_por_codigo: dict[str, Ruta] | None = None,
        excepcion_al_agregar: Exception | None = None,
        excepcion_al_eliminar: Exception | None = None,
    ):
        self._rutas_favoritas = rutas_favoritas or []
        self._ruta_por_codigo = ruta_por_codigo or {}
        self._excepcion_al_agregar = excepcion_al_agregar
        self._excepcion_al_eliminar = excepcion_al_eliminar
        self.ultima_ruta_agregada: int | None = None
        self.ultima_ruta_eliminada: int | None = None

    def buscar_cercana(self, busqueda: BusquedaRuta) -> list[Ruta]:
        raise NotImplementedError

    def obtener_ruta_por_codigo(self, codigo: str) -> Ruta | None:
        return self._ruta_por_codigo.get(codigo)

    async def calcular_caminata(self, punto_origen: Coordenada, punto_destino: Coordenada) -> Caminata:
        raise NotImplementedError

    def obtener_rutas_favoritas(self, email: str) -> list[Ruta]:
        return self._rutas_favoritas

    def agregar_ruta_favorita(self, usuario, ruta: int):
        if self._excepcion_al_agregar is not None:
            raise self._excepcion_al_agregar
        self.ultima_ruta_agregada = ruta

    def eliminar_ruta_favorita(self, usuario, ruta: int):
        if self._excepcion_al_eliminar is not None:
            raise self._excepcion_al_eliminar
        self.ultima_ruta_eliminada = ruta


class FakeRepositorioBuses(RepositorioBuses):
    """Repositorio en memoria para no depender de MongoDB en los tests.

    El caso de uso consulta el repositorio dos veces por ejecución: una con el
    `vuelta` solicitado (segmento solicitado) y otra con su negación (segmento
    opuesto). `buses_por_vuelta` permite simular buses que solo existen en uno
    de los dos segmentos.
    """

    def __init__(self, buses_por_vuelta: dict[bool, list[Bus]] | None = None):
        self._buses_por_vuelta = buses_por_vuelta or {}

    async def obtener_bus_cercano_por_ruta(self, lat: float, lon: float, ruta_id: str, vuelta: bool) -> list[Bus]:
        return self._buses_por_vuelta.get(vuelta, [])

    async def obtener_velocidad_promedio_diaria(self, empresa_id: int, numero_bus: int) -> float | None:
        return None
