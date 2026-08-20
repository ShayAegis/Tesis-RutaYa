from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.usecase.buscar_bus_cercano_por_ruta import (
    CriterioOrdenamiento,
    FiltroBuses,
    SelectorBusesConFallback,
)

SEGMENTO: list[Coordenada] = []


def _bus(numero_bus: int) -> Bus:
    return Bus(placa=f"AAA{numero_bus:03d}", numero_bus=numero_bus, empresa_id=1, ultima_ubicacion=None)


class FiltroFalso(FiltroBuses):
    def __init__(self, resultado: list[Bus]):
        self.resultado = resultado

    def filtrar(self, buses: list[Bus], segmento_ruta: list[Coordenada]) -> list[Bus]:
        return self.resultado


class FiltroQueFalla(FiltroBuses):
    def __init__(self):
        pass

    def filtrar(self, buses: list[Bus], segmento_ruta: list[Coordenada]) -> list[Bus]:
        raise AssertionError("no debería llamarse: un paso anterior ya tenía candidatos")


class CriterioFalso(CriterioOrdenamiento):
    def __init__(self, resultado: list[Bus]):
        self.resultado = resultado
        self.buses_recibidos: list[Bus] | None = None

    def ordenar(self, buses: list[Bus], segmento: list[Coordenada]) -> list[Bus]:
        self.buses_recibidos = buses
        return self.resultado


class TestSelectorBusesConFallback:
    def test_usa_el_primer_paso_si_tiene_candidatos(self):
        bus1 = _bus(1)
        bus_ordenado = _bus(99)
        criterio = CriterioFalso([bus_ordenado])
        selector = SelectorBusesConFallback([
            (FiltroFalso([bus1]), criterio, [], SEGMENTO),
            (FiltroQueFalla(), CriterioFalso([]), [], SEGMENTO),
        ])

        resultado = selector.seleccionar()

        assert resultado == [bus_ordenado]
        assert criterio.buses_recibidos == [bus1]

    def test_cae_al_segundo_paso_si_el_primero_esta_vacio(self):
        bus2 = _bus(2)
        criterio_segundo_paso = CriterioFalso([bus2])
        selector = SelectorBusesConFallback([
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
            (FiltroFalso([bus2]), criterio_segundo_paso, [], SEGMENTO),
            (FiltroQueFalla(), CriterioFalso([]), [], SEGMENTO),
        ])

        resultado = selector.seleccionar()

        assert resultado == [bus2]

    def test_cae_al_tercer_paso_si_los_dos_primeros_estan_vacios(self):
        bus3 = _bus(3)
        criterio_tercer_paso = CriterioFalso([bus3])
        selector = SelectorBusesConFallback([
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
            (FiltroFalso([bus3]), criterio_tercer_paso, [], SEGMENTO),
        ])

        resultado = selector.seleccionar()

        assert resultado == [bus3]

    def test_devuelve_lista_vacia_si_ningun_paso_tiene_candidatos(self):
        selector = SelectorBusesConFallback([
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
            (FiltroFalso([]), CriterioFalso([]), [], SEGMENTO),
        ])

        resultado = selector.seleccionar()

        assert resultado == []

    def test_no_evalua_pasos_posteriores_a_uno_con_candidatos(self):
        #FiltroQueFalla lanza una excepción si su filtrar() se llega a invocar,
        #así que si el test pasa, confirma el corte anticipado (short-circuit).
        bus1 = _bus(1)
        selector = SelectorBusesConFallback([
            (FiltroFalso([bus1]), CriterioFalso([bus1]), [], SEGMENTO),
            (FiltroQueFalla(), CriterioFalso([]), [], SEGMENTO),
        ])

        selector.seleccionar()
