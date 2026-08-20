from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.usecase.buscar_bus_cercano_por_ruta import (
    OrdenarPorCercaniaAlFinalDeSegmento,
    OrdenarPorCercaniaAlUsuario,
)
from infrastructure.services.shapely_calculador_geometria import ShapelyCalculadorGeometria

calculador = ShapelyCalculadorGeometria()

#Segmento recto norte-sur en lon=0.0, de lat=0.0 a lat=0.01 (~1.11km)
SEGMENTO = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
UBICACION_USUARIO = Coordenada(lat=0.006, lon=0.0)


def _bus(numero_bus: int, ultima_ubicacion: Coordenada) -> Bus:
    return Bus(placa=f"AAA{numero_bus:03d}", numero_bus=numero_bus, empresa_id=1, ultima_ubicacion=ultima_ubicacion)


class TestOrdenarPorCercaniaAlUsuario:
    def setup_method(self):
        self.criterio = OrdenarPorCercaniaAlUsuario(UBICACION_USUARIO, calculador)

    def test_ordena_de_mas_cercano_a_mas_lejano_del_usuario(self):
        bus_muy_cerca = _bus(1, Coordenada(lat=0.0059, lon=0.0))
        bus_medio = _bus(2, Coordenada(lat=0.004, lon=0.0))
        bus_lejos = _bus(3, Coordenada(lat=0.001, lon=0.0))

        resultado = self.criterio.ordenar([bus_lejos, bus_muy_cerca, bus_medio], SEGMENTO)

        assert resultado == [bus_muy_cerca, bus_medio, bus_lejos]

    def test_no_falla_con_lista_vacia(self):
        assert self.criterio.ordenar([], SEGMENTO) == []

    def test_no_falla_con_un_solo_bus(self):
        bus_unico = _bus(1, Coordenada(lat=0.003, lon=0.0))

        resultado = self.criterio.ordenar([bus_unico], SEGMENTO)

        assert resultado == [bus_unico]


class TestOrdenarPorCercaniaAlFinalDeSegmento:
    def setup_method(self):
        self.criterio = OrdenarPorCercaniaAlFinalDeSegmento(calculador)

    def test_ordena_de_mas_cercano_a_mas_lejano_del_final_del_segmento(self):
        bus_cerca_del_final = _bus(1, Coordenada(lat=0.009, lon=0.0))
        bus_medio = _bus(2, Coordenada(lat=0.006, lon=0.0))
        bus_lejos_del_final = _bus(3, Coordenada(lat=0.002, lon=0.0))

        resultado = self.criterio.ordenar([bus_lejos_del_final, bus_cerca_del_final, bus_medio], SEGMENTO)

        assert resultado == [bus_cerca_del_final, bus_medio, bus_lejos_del_final]

    def test_no_falla_con_lista_vacia(self):
        assert self.criterio.ordenar([], SEGMENTO) == []

    def test_no_falla_con_un_solo_bus(self):
        bus_unico = _bus(1, Coordenada(lat=0.003, lon=0.0))

        resultado = self.criterio.ordenar([bus_unico], SEGMENTO)

        assert resultado == [bus_unico]
