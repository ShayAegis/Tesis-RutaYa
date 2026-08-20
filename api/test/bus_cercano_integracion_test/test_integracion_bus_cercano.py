import pytest
from fastapi.testclient import TestClient

from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from infrastructure.dependencias import obtener_repositorio_buses, obtener_repositorio_rutas
from test.bus_cercano_integracion_test.fakes import FakeRepositorioBuses, FakeRutasRepositorio

from main import aplicacion

cliente = TestClient(aplicacion)

#Segmento recto norte-sur en lon=0.0, de lat=0.0 a lat=0.01 (~1.11km)
SEGMENTO_IDA = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
SEGMENTO_VUELTA = [Coordenada(lat=0.01, lon=0.0), Coordenada(lat=0.0, lon=0.0)]

RUTA_DE_PRUEBA = Ruta(
    id=1,
    empresa_id=1,
    empresa_nombre="Empresa Test",
    distancia_km=1.11,
    recorrido=[SEGMENTO_IDA, SEGMENTO_VUELTA],
    codigo="R1",
    paradero_inicio_id=1,
    paradero_inicio_nombre="Inicio",
    paradero_final_id=2,
    paradero_final_nombre="Final",
)

#Segmentos paralelos y distintos (offset de 0.0005 grados en lon, ~55m, fuera del buffer
#de intersección de ~35m), para simular un bus que solo existe en el segmento opuesto.
SEGMENTO_IDA_PARALELO = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
SEGMENTO_VUELTA_PARALELO = [Coordenada(lat=0.01, lon=0.0005), Coordenada(lat=0.0, lon=0.0005)]

RUTA_CON_SEGMENTOS_PARALELOS = Ruta(
    id=2,
    empresa_id=1,
    empresa_nombre="Empresa Test",
    distancia_km=1.11,
    recorrido=[SEGMENTO_IDA_PARALELO, SEGMENTO_VUELTA_PARALELO],
    codigo="R2",
    paradero_inicio_id=1,
    paradero_inicio_nombre="Inicio",
    paradero_final_id=2,
    paradero_final_nombre="Final",
)


def _bus(numero_bus: int, ultima_ubicacion: Coordenada) -> Bus:
    return Bus(placa=f"AAA{numero_bus:03d}", numero_bus=numero_bus, empresa_id=1, ultima_ubicacion=ultima_ubicacion)


def _override_repositorios(buses_por_vuelta: dict[bool, list[Bus]], ruta: Ruta | None):
    aplicacion.dependency_overrides[obtener_repositorio_buses] = lambda: FakeRepositorioBuses(buses_por_vuelta)
    aplicacion.dependency_overrides[obtener_repositorio_rutas] = lambda: FakeRutasRepositorio(ruta)


@pytest.fixture
def limpiar_overrides():
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_buses, None)
    aplicacion.dependency_overrides.pop(obtener_repositorio_rutas, None)


def test_bus_cercano_devuelve_el_bus_mas_cercano_al_usuario(limpiar_overrides):
    bus_antes_del_usuario = _bus(1, Coordenada(lat=0.003, lon=0.0))
    _override_repositorios({False: [bus_antes_del_usuario], True: []}, RUTA_DE_PRUEBA)

    respuesta = cliente.get("/rutas/R1/bus-cercano", params={"lat": 0.006, "lon": 0.0, "vuelta": False})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["numero_bus"] == 1
    assert cuerpo["empresa_id"] == 1
    assert cuerpo["ruta"] == "R1"
    assert cuerpo["eta_minutos"] > 0


def test_bus_cercano_con_vuelta_true_usa_el_segmento_de_regreso(limpiar_overrides):
    #Con vuelta=True el segmento solicitado es recorrido[1] (SEGMENTO_VUELTA, de lat=0.01 a
    #lat=0.0), así que "antes del usuario" significa más cerca de lat=0.01.
    bus_antes_del_usuario = _bus(2, Coordenada(lat=0.008, lon=0.0))
    _override_repositorios({True: [bus_antes_del_usuario], False: []}, RUTA_DE_PRUEBA)

    respuesta = cliente.get("/rutas/R1/bus-cercano", params={"lat": 0.006, "lon": 0.0, "vuelta": True})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["numero_bus"] == 2
    assert cuerpo["ruta"] == "R1"


def test_bus_cercano_sin_bus_en_segmento_solicitado_cae_al_segmento_opuesto(limpiar_overrides):
    #Ningún bus en el segmento solicitado (recorrido[0]); el único bus disponible está
    #sobre el segmento opuesto (recorrido[1], una línea paralela distinta). El caso de uso
    #completo (filtros + fallback + selector) debe encontrarlo igual, vía el endpoint real.
    bus_en_segmento_opuesto = _bus(3, Coordenada(lat=0.004, lon=0.0005))
    _override_repositorios({False: [], True: [bus_en_segmento_opuesto]}, RUTA_CON_SEGMENTOS_PARALELOS)

    respuesta = cliente.get("/rutas/R2/bus-cercano", params={"lat": 0.006, "lon": 0.0, "vuelta": False})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["numero_bus"] == 3
    assert cuerpo["ruta"] == "R2"
    assert cuerpo["eta_minutos"] > 0


def test_bus_cercano_sin_buses_disponibles_devuelve_404(limpiar_overrides):
    _override_repositorios({False: [], True: []}, RUTA_DE_PRUEBA)

    respuesta = cliente.get("/rutas/R1/bus-cercano", params={"lat": 0.006, "lon": 0.0, "vuelta": False})

    assert respuesta.status_code == 404


def test_bus_cercano_con_ruta_inexistente_devuelve_404(limpiar_overrides):
    _override_repositorios({False: [], True: []}, None)

    respuesta = cliente.get("/rutas/RUTA-INEXISTENTE/bus-cercano", params={"lat": 0.006, "lon": 0.0, "vuelta": False})

    assert respuesta.status_code == 404


def test_bus_cercano_sin_parametro_vuelta_devuelve_422(limpiar_overrides):
    _override_repositorios({False: [], True: []}, RUTA_DE_PRUEBA)

    respuesta = cliente.get("/rutas/R1/bus-cercano", params={"lat": 0.006, "lon": 0.0})

    assert respuesta.status_code == 422
