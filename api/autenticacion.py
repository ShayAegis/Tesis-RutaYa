from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends, APIRouter, status, HTTPException
from passlib.exc import InvalidTokenError

from domain.repositories.repositorio_usuarios import RepositorioUsuarios
from infrastructure.configuracion import configuracion
from infrastructure.dependencias import obtener_repositorio_usuarios
from domain.entities.usuario import Usuario
from passlib.hash import django_pbkdf2_sha256
from application.models.token import Token, TokenData, RefreshTokenRequest

from jwt import ExpiredSignatureError, encode,decode
from jwt.exceptions import ExpiredSignatureError
import secrets
import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def decodificar_token(token: str) -> TokenData:
    excepcion_credenciales = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="No se pudo validar las credenciales",
                                headers={"WWW-Authenticate": "Bearer"})
    excepcion_token_vencido = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                            detail="El token de acceso ha vencido",
                                            headers={"WWW-Authenticate":'Bearer error="invalid_token",error_description="The access token expired"'})
    try:
        token_decodificado = decode(token,
                                    configuracion.oauth2_secret_key,
                                    configuracion.oauth2_algorithm)
        username: str | None = token_decodificado.get("sub")
        expiracion: int | None = token_decodificado.get("exp")
     
        if not username:
            # Se envía ese header porque es parte del estándar de autenticación HTTP
            # para indicar al cliente qué tipo de autenticación requiere el recurso.
            raise excepcion_credenciales
    # Esta excepcion incluye el caso en que el token haya expirado
    except InvalidTokenError:
        raise excepcion_credenciales
    except ExpiredSignatureError:
        raise excepcion_token_vencido

    return TokenData(username=username,expiration=expiracion)


async def obtener_usuario_actual(token: Annotated[str,Depends(oauth2_scheme)],
                                 repositorio = Depends(obtener_repositorio_usuarios)) -> Usuario:
    datos_token = decodificar_token(token)
    email = datos_token.username
    usuario = repositorio.obtener_usuario_por_correo(email)
    return usuario

def crear_token_acceso(data:dict,expiracion:timedelta | None = None) -> str:
    data_a_codificar = data.copy()
    if expiracion:
        expiracion_timestamp = datetime.now(timezone.utc) + expiracion
        data_a_codificar.update({"exp":expiracion_timestamp})
    else:
        expiracion_timestamp = datetime.now(timezone.utc) + timedelta(minutes=5)
        data_a_codificar.update({"exp":expiracion_timestamp})
    return encode(data_a_codificar,
                  configuracion.oauth2_secret_key,
                  configuracion.oauth2_algorithm)

def crear_token_refresco() -> str:
    token_refresco = secrets.token_urlsafe(32)
    return token_refresco
enrutador = APIRouter()

@enrutador.post("/login",response_model=Token,status_code=status.HTTP_200_OK,tags=["login"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],
                repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios)
                ) -> Token:
    usuario_existe = repositorio.usuario_existe(form_data.username)
    if not usuario_existe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Correo electrónico o contraseña incorrecta")
    usuario = repositorio.obtener_usuario_por_correo(form_data.username)
    if not django_pbkdf2_sha256.verify(form_data.password, usuario.contrasenia):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Correo electrónico o contraseña incorrecta")
    repositorio.actualizar_ultimo_login(usuario.email)
    tiempo_expiracion_token = timedelta(minutes=configuracion.oauth2_access_token_expiration_minutes)
    token_refresco = crear_token_refresco()
    token_refresco_hash = hashlib.sha256(token_refresco.encode()).hexdigest()
    fecha_expiracion_token_refresco = datetime.now(timezone.utc) + timedelta(days=configuracion.oauth2_refresh_token_expiration_days)
    repositorio.guardar_token_refresco(usuario,token_refresco_hash,fecha_expiracion_token_refresco)
    token_acceso = crear_token_acceso({"sub": usuario.email},tiempo_expiracion_token)
    return Token(access_token=token_acceso,refresh_token=token_refresco,token_type="bearer")

@enrutador.post("/refresh", response_model=Token,status_code=status.HTTP_200_OK, tags=["login"])
async def refresh(datos: RefreshTokenRequest,
                  repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios)):
    refresh_token_hash = hashlib.sha256(datos.refresh_token.encode()).hexdigest()
    usuario = repositorio.usar_token_refresco(refresh_token_hash)
    if usuario is None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED,detail={"error":"El refresh_token enviado está vencido"})
    tiempo_expiracion_token = timedelta(minutes=configuracion.oauth2_access_token_expiration_minutes)
    token_refresco = crear_token_refresco()
    token_refresco_hash = hashlib.sha256(token_refresco.encode()).hexdigest()
    fecha_expiracion_token_refresco = datetime.now(timezone.utc) + timedelta(
        days=configuracion.oauth2_refresh_token_expiration_days)
    repositorio.guardar_token_refresco(usuario, token_refresco_hash, fecha_expiracion_token_refresco)
    token_acceso = crear_token_acceso({"sub":usuario.email},tiempo_expiracion_token)
    return Token(access_token=token_acceso,refresh_token=token_refresco,token_type="bearer")



