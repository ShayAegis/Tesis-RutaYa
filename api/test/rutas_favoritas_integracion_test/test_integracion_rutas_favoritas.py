import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from autenticacion import obtener_usuario_actual
from domain.entities.bus import Bus
from domain.entities.coordenada import Coordenada
from domain.entities.ruta import Ruta
from domain.entities.usuario import Usuario
from domain.usecase.eliminar_ruta_favorita import RutaNoFavoritaError
from infrastructure.dependencias import obtener_repositorio_buses, obtener_repositorio_rutas
from test.rutas_favoritas_integracion_test.fakes import FakeRepositorioBuses, FakeRutasRepositorio

from main import aplicacion

cliente = TestClient(aplicacion)

USUARIO_ACTUAL = Usuario(id=1, email="juan@example.com", nombres="Juan", apellidos="Perez", contrasenia="hash")

#Segmento recto norte-sur en lon=0.0, de lat=0.0 a lat=0.01 (~1.11km)
SEGMENTO_IDA = [Coordenada(lat=0.0, lon=0.0), Coordenada(lat=0.01, lon=0.0)]
SEGMENTO_VUELTA = [Coordenada(lat=0.01, lon=0.0), Coordenada(lat=0.0, lon=0.0)]

RUTA_FAVORITA = Ruta(
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


def _bus(numero_bus: int, ultima_ubicacion: Coordenada) -> Bus:
    return Bus(placa=f"AAA{numero_bus:03d}", numero_bus=numero_bus, empresa_id=1, ultima_ubicacion=ultima_ubicacion)


@pytest.fixture
def autenticado():
    aplicacion.dependency_overrides[obtener_usuario_actual] = lambda: USUARIO_ACTUAL
    yield
    aplicacion.dependency_overrides.pop(obtener_usuario_actual, None)


@pytest.fixture
def limpiar_overrides_repositorios():
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_rutas, None)
    aplicacion.dependency_overrides.pop(obtener_repositorio_buses, None)


def _override_repositorio_rutas(**kwargs):
    aplicacion.dependency_overrides[obtener_repositorio_rutas] = lambda: FakeRutasRepositorio(**kwargs)


def _override_repositorio_buses(buses_por_vuelta: dict[bool, list[Bus]] | None = None):
    aplicacion.dependency_overrides[obtener_repositorio_buses] = lambda: FakeRepositorioBuses(buses_por_vuelta)


class TestObtenerRutasFavoritas:
    def test_sin_autenticacion_devuelve_401(self, limpiar_overrides_repositorios):
        _override_repositorio_rutas(rutas_favoritas=[RUTA_FAVORITA])

        respuesta = cliente.get("/usuarios/me/rutas/favoritas")

        assert respuesta.status_code == 401

    def test_sin_posicion_devuelve_metadata_sin_bus_cercano(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas(rutas_favoritas=[RUTA_FAVORITA])

        respuesta = cliente.get("/usuarios/me/rutas/favoritas")

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert len(cuerpo) == 1
        assert cuerpo[0]["metadata"]["codigo"] == "R1"
        assert cuerpo[0]["bus_cercano"] is None

    def test_con_posicion_incluye_el_bus_cercano_mas_proximo(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas(rutas_favoritas=[RUTA_FAVORITA], ruta_por_codigo={"R1": RUTA_FAVORITA})
        bus_antes_del_usuario = _bus(1, Coordenada(lat=0.003, lon=0.0))
        _override_repositorio_buses({False: [bus_antes_del_usuario], True: []})

        respuesta = cliente.get(
            "/usuarios/me/rutas/favoritas",
            params={"posicion_actual_lat": 0.006, "posicion_actual_lon": 0.0},
        )

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo[0]["bus_cercano"]["numero_bus"] == 1
        assert cuerpo[0]["bus_cercano"]["eta_minutos"] > 0

    def test_con_posicion_sin_buses_disponibles_bus_cercano_es_none(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas(rutas_favoritas=[RUTA_FAVORITA], ruta_por_codigo={"R1": RUTA_FAVORITA})
        _override_repositorio_buses({False: [], True: []})

        respuesta = cliente.get(
            "/usuarios/me/rutas/favoritas",
            params={"posicion_actual_lat": 0.006, "posicion_actual_lon": 0.0},
        )

        assert respuesta.status_code == 200
        cuerpo = respuesta.json()
        assert cuerpo[0]["bus_cercano"] is None


class TestAgregarRutaFavorita:
    def test_sin_autenticacion_devuelve_401(self, limpiar_overrides_repositorios):
        _override_repositorio_rutas()

        respuesta = cliente.put("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 401

    def test_agregar_ruta_favorita_devuelve_200(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas()

        respuesta = cliente.put("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 200

    def test_agregar_ruta_favorita_ya_existente_devuelve_409(self, autenticado, limpiar_overrides_repositorios):
        excepcion = IntegrityError("stmt", {}, Exception("duplicado"))
        _override_repositorio_rutas(excepcion_al_agregar=excepcion)

        respuesta = cliente.put("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 409

    def test_agregar_ruta_favorita_error_generico_devuelve_400(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas(excepcion_al_agregar=RuntimeError("fallo inesperado"))

        respuesta = cliente.put("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 400


class TestEliminarRutaFavorita:
    def test_sin_autenticacion_devuelve_401(self, limpiar_overrides_repositorios):
        _override_repositorio_rutas()

        respuesta = cliente.delete("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 401

    def test_eliminar_ruta_favorita_devuelve_204(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas()

        respuesta = cliente.delete("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 204

    def test_eliminar_ruta_que_no_era_favorita_devuelve_404(self, autenticado, limpiar_overrides_repositorios):
        _override_repositorio_rutas(excepcion_al_eliminar=RutaNoFavoritaError(1))

        respuesta = cliente.delete("/usuarios/me/rutas/favoritas/1")

        assert respuesta.status_code == 404
