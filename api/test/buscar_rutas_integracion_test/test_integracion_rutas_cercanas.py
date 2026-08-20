import pytest

from fastapi.testclient import TestClient
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from infrastructure.dependencias import obtener_repositorio_rutas
from test.buscar_rutas_integracion_test.fakes import FakeRutasRepositorio


from main import aplicacion

cliente = TestClient(aplicacion)


RUTAS_DE_PRUEBA = [
    Ruta(
        id=4,
        empresa_id=1,
        empresa_nombre="Empresa Test",
        distancia_km=1.11,
        recorrido=[
            [Coordenada(lat=7.88919, lon=-72.541874), Coordenada(lat=7.813657, lon=-72.516418)],
            [Coordenada(lat=7.813657, lon=-72.516418), Coordenada(lat=7.88919, lon=-72.541874)],
        ],
        codigo="R1",
        paradero_inicio_id=3,
        paradero_inicio_nombre="Nuevo Horizonte",
        paradero_final_id=6,
        paradero_final_nombre="Villas de San Diego",
    ),
]


@pytest.fixture
def repositorio_con_rutas():
    aplicacion.dependency_overrides[obtener_repositorio_rutas] = lambda: FakeRutasRepositorio(RUTAS_DE_PRUEBA)
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_rutas, None)


@pytest.fixture
def repositorio_sin_rutas():
    aplicacion.dependency_overrides[obtener_repositorio_rutas] = lambda: FakeRutasRepositorio([])
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_rutas, None)

@pytest.mark.parametrize(
    "punto_origen,punto_destino,distancia_caminata",
    [(None, None,None),
     (Coordenada(lat=7.88919, lon=-72.541874), None,None),
     (None, Coordenada(lat=7.813657, lon=-72.516418),500),
     (Coordenada(lat=7.88919, lon=-72.541874),Coordenada(lat=7.813657, lon=-72.516418),None)]
)
def test_sin_parametros_de_entrada(punto_origen:Coordenada|None, punto_destino:Coordenada|None,distancia_caminata: int | float | None):
    respuesta = cliente.get("/rutas/buscar-cercana",params={
        "origin_lat": punto_origen.lat if punto_origen is not None else "",
        "origin_lon": punto_origen.lon if punto_origen is not None else "",
        "dest_lat": punto_destino.lat if punto_destino is not None else "",
        "dest_lon": punto_destino.lon if punto_destino is not None else "",
        "distancia_caminata": distancia_caminata if distancia_caminata is not None else "",
    })
    assert respuesta.status_code == 422

@pytest.mark.parametrize(
    "punto_origen,punto_destino,distancia_caminata",
    [(Coordenada(lat=7.8190493, lon=-72.5149420),Coordenada(lat=7.8190493, lon=-72.5149420),500),
     (Coordenada(lat=7.8190356, lon=-72.514944),Coordenada(lat=7.816911, lon=-72.515684),500)]
)
def test_puntos_muy_cercanos(punto_origen:Coordenada,punto_destino:Coordenada,distancia_caminata: int | float):
    respuesta = cliente.get("/rutas/buscar-cercana",params={
        "origin_lat": punto_origen.lat,
        "origin_lon": punto_origen.lon,
        "dest_lat": punto_destino.lat,
        "dest_lon": punto_destino.lon,
        "distancia_caminata": distancia_caminata,
    })
    assert respuesta.status_code == 400


def test_buscar_ruta_cercana_devuelve_rutas_encontradas(repositorio_con_rutas):
    respuesta = cliente.get("/rutas/buscar-cercana", params={
        "origin_lat": 7.88919,
        "origin_lon": -72.541874,
        "dest_lat": 7.813657,
        "dest_lon": -72.516418,
        "distancia_caminata": 500,
    })
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["metadata"]["codigo"] == "R1"
    assert cuerpo[0]["metadata"]["empresa"] == "Empresa Test"


def test_buscar_ruta_cercana_sin_rutas_devuelve_404(repositorio_sin_rutas):
    respuesta = cliente.get("/rutas/buscar-cercana", params={
        "origin_lat": 7.88919,
        "origin_lon": -72.541874,
        "dest_lat": 7.813657,
        "dest_lon": -72.516418,
        "distancia_caminata": 500,
    })
    assert respuesta.status_code == 404
