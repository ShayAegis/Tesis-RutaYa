import pytest

from fastapi.testclient import TestClient

from infrastructure.dependencias import obtener_repositorio_usuarios
from test.usuarios_integracion_test.fakes import FakeRepositorioUsuarios

from main import aplicacion

cliente = TestClient(aplicacion)


@pytest.fixture
def repositorio_sin_usuarios():
    aplicacion.dependency_overrides[obtener_repositorio_usuarios] = lambda: FakeRepositorioUsuarios()
    yield
    aplicacion.dependency_overrides.pop(obtener_repositorio_usuarios, None)


DATOS_VALIDOS = {
    "nombres": "Juan",
    "apellidos": "Perez",
    "email": "juan.perez@example.com",
    "contrasenia": "Clave1234",
}


@pytest.mark.parametrize("campo_vacio", ["nombres", "apellidos", "email", "contrasenia"])
def test_crear_usuario_con_campo_vacio_devuelve_422(repositorio_sin_usuarios, campo_vacio):
    datos = {**DATOS_VALIDOS, campo_vacio: ""}

    respuesta = cliente.post("/usuarios/", json=datos)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", campo_vacio],
                "msg": "Field required",
                "input": datos,
            }
        ]
    }


def test_crear_usuario_con_varios_campos_vacios_devuelve_422_por_cada_uno(repositorio_sin_usuarios):
    datos = {**DATOS_VALIDOS, "nombres": "", "email": ""}

    respuesta = cliente.post("/usuarios/", json=datos)

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    campos_reportados = [error["loc"][1] for error in cuerpo["detail"]]
    assert campos_reportados == ["nombres", "email"]


def test_crear_usuario_con_datos_validos_devuelve_201(repositorio_sin_usuarios):
    respuesta = cliente.post("/usuarios/", json=DATOS_VALIDOS)

    assert respuesta.status_code == 201
