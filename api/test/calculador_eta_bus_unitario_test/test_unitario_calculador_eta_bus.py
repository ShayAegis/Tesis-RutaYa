import asyncio

from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.servicios.calculador_eta_bus import VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS, CalculadorEtaBus
from infrastructure.services.shapely_calculador_geometria import ShapelyCalculadorGeometria

calculador_geometria = ShapelyCalculadorGeometria()

#Segmento solicitado: recto norte-sur en lon=0.0, de lat=0.0 a lat=0.01 (~1.11km)
SEGMENTO_SOLICITADO = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
#Segmento opuesto: paralelo, recorrido en sentido contrario, offset 0.0005 grados en lon (~55m,
#fuera del buffer de intersección de ~35m con el segmento solicitado)
SEGMENTO_OPUESTO = [Coordenada(lat=0.01, lon=0.0005), Coordenada(lat=0.0, lon=0.0005)]
UBICACION_USUARIO = Coordenada(lat=0.006, lon=0.0)


class RepositorioBusesFalso(RepositorioBuses):
    def __init__(self, velocidad_promedio_kmh: float | None):
        self.velocidad_promedio_kmh = velocidad_promedio_kmh

    async def obtener_bus_cercano_por_ruta(self, lat, lon, ruta_id, vuelta) -> list[Bus]:
        return []

    async def obtener_velocidad_promedio_diaria(self, empresa_id: int, numero_bus: int) -> float | None:
        return self.velocidad_promedio_kmh


def _bus(ultima_ubicacion: Coordenada) -> Bus:
    return Bus(placa="AAA000", numero_bus=1, empresa_id=1, ultima_ubicacion=ultima_ubicacion)


def _calcular(calculador_eta: CalculadorEtaBus, bus: Bus) -> float:
    return asyncio.run(
        calculador_eta.calcular(bus, SEGMENTO_SOLICITADO, SEGMENTO_OPUESTO, UBICACION_USUARIO),
    )


def _distancia_esperada_segundos(distancia_metros: float, velocidad_ms: float) -> float:
    return round((distancia_metros / velocidad_ms) / 60, 1)


class TestCalculadorEtaBus:
    def test_usa_velocidad_real_del_bus_cuando_esta_disponible(self):
        #36 km/h == 10 m/s, para que la conversión sea exacta
        calculador_eta = CalculadorEtaBus(calculador_geometria, RepositorioBusesFalso(velocidad_promedio_kmh=36))
        bus_antes_del_usuario = _bus(Coordenada(lat=0.003, lon=0.0))

        eta_minutos = _calcular(calculador_eta, bus_antes_del_usuario)

        distancia_metros = calculador_geometria.longitud_metros(
            calculador_geometria.subtrayecto(SEGMENTO_SOLICITADO, 0.003, 0.006),
        )
        assert eta_minutos == _distancia_esperada_segundos(distancia_metros, 10.0)

    def test_usa_velocidad_fallback_cuando_no_hay_velocidad_real(self):
        calculador_eta = CalculadorEtaBus(calculador_geometria, RepositorioBusesFalso(velocidad_promedio_kmh=None))
        bus_antes_del_usuario = _bus(Coordenada(lat=0.003, lon=0.0))

        eta_minutos = _calcular(calculador_eta, bus_antes_del_usuario)

        distancia_metros = calculador_geometria.longitud_metros(
            calculador_geometria.subtrayecto(SEGMENTO_SOLICITADO, 0.003, 0.006),
        )
        assert eta_minutos == _distancia_esperada_segundos(distancia_metros, VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS)

    def test_bus_que_ya_paso_al_usuario_debe_dar_toda_la_vuelta(self):
        calculador_eta = CalculadorEtaBus(calculador_geometria, RepositorioBusesFalso(velocidad_promedio_kmh=None))
        bus_despues_del_usuario = _bus(Coordenada(lat=0.008, lon=0.0))

        eta_minutos = _calcular(calculador_eta, bus_despues_del_usuario)

        distancia_metros = (
            calculador_geometria.longitud_metros(calculador_geometria.subtrayecto(SEGMENTO_SOLICITADO, 0.008, 0.01))
            + calculador_geometria.longitud_metros(SEGMENTO_OPUESTO)
            + calculador_geometria.longitud_metros(calculador_geometria.subtrayecto(SEGMENTO_SOLICITADO, 0.0, 0.006))
        )
        assert eta_minutos == _distancia_esperada_segundos(distancia_metros, VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS)

    def test_bus_en_el_segmento_opuesto(self):
        calculador_eta = CalculadorEtaBus(calculador_geometria, RepositorioBusesFalso(velocidad_promedio_kmh=None))
        #Sobre el segmento opuesto, que empieza en lat=0.01 y termina en lat=0.0
        bus_en_segmento_opuesto = _bus(Coordenada(lat=0.004, lon=0.0005))

        eta_minutos = _calcular(calculador_eta, bus_en_segmento_opuesto)

        distancia_metros = (
            calculador_geometria.longitud_metros(calculador_geometria.subtrayecto(SEGMENTO_OPUESTO, 0.006, 0.01))
            + calculador_geometria.longitud_metros(calculador_geometria.subtrayecto(SEGMENTO_SOLICITADO, 0.0, 0.006))
        )
        assert eta_minutos == _distancia_esperada_segundos(distancia_metros, VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS)

    def test_bus_fuera_de_ambos_segmentos_usa_distancia_en_linea_recta(self):
        calculador_eta = CalculadorEtaBus(calculador_geometria, RepositorioBusesFalso(velocidad_promedio_kmh=None))
        bus_fuera_de_ruta = _bus(Coordenada(lat=0.003, lon=1.0))

        eta_minutos = _calcular(calculador_eta, bus_fuera_de_ruta)

        distancia_metros = calculador_geometria.distancia_puntos_metros(
            Coordenada(lat=0.003, lon=1.0), UBICACION_USUARIO,
        )
        assert eta_minutos == _distancia_esperada_segundos(distancia_metros, VELOCIDAD_PROMEDIO_BUS_FALLBACK_MS)
