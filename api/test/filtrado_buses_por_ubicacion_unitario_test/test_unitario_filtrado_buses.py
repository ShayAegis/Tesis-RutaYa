from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.usecase.buscar_bus_cercano_por_ruta import (
    FiltroBusesEnSegmentoOpuesto,
    FiltroBusesEnSegmentoSolicitado,
    FiltroBusesYaPasaronEnSegmentoSolicitado,
)
from infrastructure.services.shapely_calculador_geometria import ShapelyCalculadorGeometria

calculador = ShapelyCalculadorGeometria()

#Segmento recto norte-sur en lon=0.0, de lat=0.0 a lat=0.01 (~1.11km)
SEGMENTO = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
UBICACION_USUARIO = Coordenada(lat=0.006, lon=0.0)


def _bus(numero_bus: int, ultima_ubicacion: Coordenada | None) -> Bus:
    return Bus(placa=f"AAA{numero_bus:03d}", numero_bus=numero_bus, empresa_id=1, ultima_ubicacion=ultima_ubicacion)


class TestFiltroBusesEnSegmentoSolicitado:
    def setup_method(self):
        self.filtro = FiltroBusesEnSegmentoSolicitado(UBICACION_USUARIO, calculador)

    def test_incluye_bus_sobre_el_segmento_y_antes_del_usuario(self):
        bus_antes_del_usuario = _bus(1, Coordenada(lat=0.003, lon=0.0))

        resultado = self.filtro.filtrar([bus_antes_del_usuario], SEGMENTO)

        assert resultado == [bus_antes_del_usuario]

    def test_excluye_bus_sobre_el_segmento_pero_despues_del_usuario(self):
        bus_despues_del_usuario = _bus(1, Coordenada(lat=0.008, lon=0.0))

        resultado = self.filtro.filtrar([bus_despues_del_usuario], SEGMENTO)

        assert resultado == []

    def test_excluye_bus_fuera_del_buffer_de_interseccion(self):
        #A 0.001 grados del segmento (~110m), fuera del buffer de ~35m
        bus_lejos_del_segmento = _bus(1, Coordenada(lat=0.003, lon=0.001))

        resultado = self.filtro.filtrar([bus_lejos_del_segmento], SEGMENTO)

        assert resultado == []

    def test_incluye_bus_dentro_del_buffer_de_interseccion(self):
        #A 0.0001 grados del segmento (~11m), dentro del buffer de ~35m
        bus_cerca_del_segmento = _bus(1, Coordenada(lat=0.003, lon=0.0001))

        resultado = self.filtro.filtrar([bus_cerca_del_segmento], SEGMENTO)

        assert resultado == [bus_cerca_del_segmento]

    def test_excluye_bus_sin_ultima_ubicacion(self):
        bus_sin_ubicacion = _bus(1, None)

        resultado = self.filtro.filtrar([bus_sin_ubicacion], SEGMENTO)

        assert resultado == []

    def test_conserva_solo_los_buses_validos_entre_varios(self):
        bus_valido = _bus(1, Coordenada(lat=0.002, lon=0.0))
        bus_despues_del_usuario = _bus(2, Coordenada(lat=0.009, lon=0.0))
        bus_fuera_de_ruta = _bus(3, Coordenada(lat=0.002, lon=1.0))
        bus_sin_ubicacion = _bus(4, None)

        resultado = self.filtro.filtrar(
            [bus_valido, bus_despues_del_usuario, bus_fuera_de_ruta, bus_sin_ubicacion], SEGMENTO,
        )

        assert resultado == [bus_valido]


class TestFiltroBusesYaPasaronEnSegmentoSolicitado:
    def setup_method(self):
        self.filtro = FiltroBusesYaPasaronEnSegmentoSolicitado(UBICACION_USUARIO, calculador)

    def test_incluye_bus_sobre_el_segmento_y_despues_del_usuario(self):
        bus_despues_del_usuario = _bus(1, Coordenada(lat=0.008, lon=0.0))

        resultado = self.filtro.filtrar([bus_despues_del_usuario], SEGMENTO)

        assert resultado == [bus_despues_del_usuario]

    def test_excluye_bus_sobre_el_segmento_pero_antes_del_usuario(self):
        bus_antes_del_usuario = _bus(1, Coordenada(lat=0.003, lon=0.0))

        resultado = self.filtro.filtrar([bus_antes_del_usuario], SEGMENTO)

        assert resultado == []

    def test_incluye_bus_exactamente_en_la_proyeccion_del_usuario(self):
        #Caso borde complementario al de FiltroBusesEnSegmentoSolicitado: cuando la
        #proyección coincide exactamente, este filtro sí lo considera "ya pasado".
        bus_en_la_proyeccion_del_usuario = _bus(1, Coordenada(lat=0.006, lon=0.0))

        resultado = self.filtro.filtrar([bus_en_la_proyeccion_del_usuario], SEGMENTO)

        assert resultado == [bus_en_la_proyeccion_del_usuario]

    def test_excluye_bus_fuera_del_buffer_de_interseccion(self):
        bus_lejos_del_segmento = _bus(1, Coordenada(lat=0.008, lon=0.001))

        resultado = self.filtro.filtrar([bus_lejos_del_segmento], SEGMENTO)

        assert resultado == []

    def test_excluye_bus_sin_ultima_ubicacion(self):
        bus_sin_ubicacion = _bus(1, None)

        resultado = self.filtro.filtrar([bus_sin_ubicacion], SEGMENTO)

        assert resultado == []

    def test_conserva_solo_los_buses_validos_entre_varios(self):
        bus_valido = _bus(1, Coordenada(lat=0.009, lon=0.0))
        bus_antes_del_usuario = _bus(2, Coordenada(lat=0.002, lon=0.0))
        bus_fuera_de_ruta = _bus(3, Coordenada(lat=0.009, lon=1.0))
        bus_sin_ubicacion = _bus(4, None)

        resultado = self.filtro.filtrar(
            [bus_valido, bus_antes_del_usuario, bus_fuera_de_ruta, bus_sin_ubicacion], SEGMENTO,
        )

        assert resultado == [bus_valido]


class TestFiltroBusesEnSegmentoOpuesto:
    def setup_method(self):
        self.filtro = FiltroBusesEnSegmentoOpuesto(UBICACION_USUARIO, calculador)

    def test_incluye_bus_sobre_el_segmento_sin_importar_su_proyeccion(self):
        #A diferencia del filtro del segmento solicitado, aquí no importa si el bus
        #está "antes" o "después" de la proyección del usuario: cualquier bus sobre
        #el segmento opuesto es un candidato válido.
        bus_al_final_del_segmento = _bus(1, Coordenada(lat=0.009, lon=0.0))

        resultado = self.filtro.filtrar([bus_al_final_del_segmento], SEGMENTO)

        assert resultado == [bus_al_final_del_segmento]

    def test_excluye_bus_fuera_del_buffer_de_interseccion(self):
        bus_lejos_del_segmento = _bus(1, Coordenada(lat=0.003, lon=0.001))

        resultado = self.filtro.filtrar([bus_lejos_del_segmento], SEGMENTO)

        assert resultado == []

    def test_excluye_bus_sin_ultima_ubicacion(self):
        bus_sin_ubicacion = _bus(1, None)

        resultado = self.filtro.filtrar([bus_sin_ubicacion], SEGMENTO)

        assert resultado == []
