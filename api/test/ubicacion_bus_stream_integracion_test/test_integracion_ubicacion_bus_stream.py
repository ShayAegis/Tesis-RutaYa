import json

import pytest
from fastapi.testclient import TestClient

from infrastructure.configuracion import configuracion
from infrastructure.dependencias import obtener_repositorio_transmision_ubicacion_bus
from test.ubicacion_bus_stream_integracion_test.fakes import FakeRepositorioTransmisionUbicacionBus

from main import aplicacion

cliente = TestClient(aplicacion)


def _mensaje(lat=7.1, lon=-72.5, velocidad=10.5, azimut=90.0, timestamp="2026-08-20T10:00:00Z") -> bytes:
    return json.dumps({
        "lat": lat, "lon": lon, "velocidad": velocidad, "azimut": azimut, "timestamp": timestamp,
    }).encode()


def _leer_eventos(respuesta) -> list[dict]:
    eventos = []
    for linea in respuesta.iter_lines():
        if linea.startswith("data: "):
            eventos.append(json.loads(linea[len("data: "):]))
    return eventos


@pytest.fixture
def limpiar_override():
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_transmision_ubicacion_bus, None)


def test_reenvia_una_actualizacion_de_ubicacion(limpiar_override):
    fake = FakeRepositorioTransmisionUbicacionBus([_mensaje(lat=7.1, lon=-72.5, velocidad=10.5, azimut=90.0)])
    aplicacion.dependency_overrides[obtener_repositorio_transmision_ubicacion_bus] = lambda: fake

    with cliente.stream("GET", "/buses/5/ubicacion/stream", params={"empresaId": 1, "rutaId": "R1"}) as respuesta:
        assert respuesta.status_code == 200
        eventos = _leer_eventos(respuesta)

    assert eventos == [{
        "lat": 7.1, "lon": -72.5, "velocidad": 10.5, "azimut": 90.0, "timestamp": "2026-08-20T10:00:00Z",
    }]


def test_reenvia_multiples_actualizaciones_en_orden(limpiar_override):
    mensajes = [_mensaje(lat=lat) for lat in (7.1, 7.2, 7.3)]
    fake = FakeRepositorioTransmisionUbicacionBus(mensajes)
    aplicacion.dependency_overrides[obtener_repositorio_transmision_ubicacion_bus] = lambda: fake

    with cliente.stream("GET", "/buses/5/ubicacion/stream", params={"empresaId": 1, "rutaId": "R1"}) as respuesta:
        eventos = _leer_eventos(respuesta)

    assert [evento["lat"] for evento in eventos] == [7.1, 7.2, 7.3]


def test_se_suscribe_al_tema_construido_con_empresa_ruta_y_bus(limpiar_override):
    fake = FakeRepositorioTransmisionUbicacionBus([])
    aplicacion.dependency_overrides[obtener_repositorio_transmision_ubicacion_bus] = lambda: fake

    with cliente.stream("GET", "/buses/5/ubicacion/stream", params={"empresaId": 1, "rutaId": "R1"}) as respuesta:
        list(respuesta.iter_lines())

    assert fake.temas_recibidos == [f"{configuracion.mqtt_basetopic}/1/R1/5"]


def test_sin_empresa_id_devuelve_422(limpiar_override):
    fake = FakeRepositorioTransmisionUbicacionBus([])
    aplicacion.dependency_overrides[obtener_repositorio_transmision_ubicacion_bus] = lambda: fake

    respuesta = cliente.get("/buses/5/ubicacion/stream", params={"rutaId": "R1"})

    assert respuesta.status_code == 422


def test_stream_vacio_se_cierra_sin_eventos(limpiar_override):
    fake = FakeRepositorioTransmisionUbicacionBus([])
    aplicacion.dependency_overrides[obtener_repositorio_transmision_ubicacion_bus] = lambda: fake

    with cliente.stream("GET", "/buses/5/ubicacion/stream", params={"empresaId": 1, "rutaId": "R1"}) as respuesta:
        assert respuesta.status_code == 200
        eventos = _leer_eventos(respuesta)

    assert eventos == []
