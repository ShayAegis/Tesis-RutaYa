import asyncio

from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import django_pbkdf2_sha256

from application.models.token import RefreshTokenRequest
from autenticacion import decodificar_token, login, refresh
from domain.entities.usuario import Usuario
from test.autenticacion_unitario_test.fakes import FakeRepositorioUsuarios

EMAIL = "juan@example.com"
CONTRASENIA_EN_CLARO = "ClaveSegura123"


def _usuario_de_prueba() -> Usuario:
    return Usuario(
        id=1,
        email=EMAIL,
        nombres="Juan",
        apellidos="Perez",
        contrasenia=django_pbkdf2_sha256.hash(CONTRASENIA_EN_CLARO),
    )


async def _login_y_refresh():
    repositorio = FakeRepositorioUsuarios([_usuario_de_prueba()])

    formulario = OAuth2PasswordRequestForm(username=EMAIL, password=CONTRASENIA_EN_CLARO)
    token_login = await login(formulario, repositorio)

    datos_token_login = decodificar_token(token_login.access_token)

    datos_refresh = RefreshTokenRequest(refresh_token=token_login.refresh_token)
    token_refrescado = await refresh(datos_refresh, repositorio)

    datos_token_refrescado = decodificar_token(token_refrescado.access_token)

    return token_login, datos_token_login, token_refrescado, datos_token_refrescado


def test_login_devuelve_tokens_validos_y_refresh_los_renueva_para_el_mismo_usuario():
    token_login, datos_token_login, token_refrescado, datos_token_refrescado = asyncio.run(_login_y_refresh())

    #login: el access_token emitido decodifica al email correcto
    assert token_login.token_type == "bearer"
    assert datos_token_login.username == EMAIL

    #refresh: el nuevo access_token también decodifica al mismo usuario
    assert token_refrescado.token_type == "bearer"
    assert datos_token_refrescado.username == EMAIL

    #el refresh_token se rota: el nuevo es distinto del usado para pedirlo
    assert token_refrescado.refresh_token != token_login.refresh_token
