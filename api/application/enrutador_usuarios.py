from typing import Annotated, List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError

from application.dto.rutas_dto import BusCercanoDTO, RutaFavoritaDTO
from application.dto.usuario_dto import UsuarioCreadoDTO, UsuarioDTO
from application.models.error_response import ErrorResponse
from domain.entities.ruta import Ruta
from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_usuarios import RepositorioUsuarios
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.servicios.calculador_geometria import CalculadorGeometria
from domain.usecase.agregar_ruta_favorita import AgregarRutaFavorita
from domain.usecase.buscar_bus_cercano_por_ruta import BuscarBusCercanoPorRuta
from domain.usecase.crear_usuario import CrearUsuario, UsuarioYaExisteError
from domain.usecase.eliminar_ruta_favorita import EliminarRutaFavorita
from domain.usecase.obtener_rutas_favoritas import ObtenerRutasFavoritas
from infrastructure.dependencias import (
    obtener_calculador_geometria,
    obtener_repositorio_buses,
    obtener_repositorio_rutas,
    obtener_repositorio_usuarios,
)
from domain.entities.usuario import Usuario
from domain.exceptions.contrasenia_invalida_excepcion import ContraseniaInvalidaError
from autenticacion import obtener_usuario_actual

enrutador = APIRouter(prefix="/usuarios",tags=["usuarios"])

@enrutador.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioCreadoDTO,
    responses={
        400: {"model": ErrorResponse, "description": "La contraseña no cumple la política de seguridad"},
        409: {"model": ErrorResponse, "description": "El email ya está registrado"},
        422: {"description": "Falta un campo requerido o fue enviado vacío"},
    },
)
async def crear_usuario(
    datos: UsuarioDTO,
    repositorio: RepositorioUsuarios = Depends(obtener_repositorio_usuarios),
):
    campos_vacios = [
        campo for campo in ("nombres", "apellidos", "email", "contrasenia")
        if getattr(datos, campo) == ""
    ]
    if campos_vacios:
        errores = [
            {
                "type": "missing",
                "loc": ["body", campo],
                "msg": "Field required",
                "input": datos.model_dump(),
            }
            for campo in campos_vacios
        ]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=errores)

    nuevo_usuario = Usuario(
        id=None,
        email=datos.email,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        contrasenia=datos.contrasenia,
    )

    caso_uso = CrearUsuario(repositorio)
    try:
        usuario_creado = caso_uso.ejecutar(nuevo_usuario)
    except UsuarioYaExisteError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese email",
        )
    except ContraseniaInvalidaError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese email",
        )

    return UsuarioCreadoDTO.desde_dominio(usuario_creado)

async def _bus_cercano_para_favorita(
    caso_uso_bus_cercano: BuscarBusCercanoPorRuta, ruta: Ruta, lat: float, lon: float,
) -> BusCercanoDTO | None:
    candidatos = [
        await caso_uso_bus_cercano.ejecutar(lat, lon, ruta.codigo, vuelta)
        for vuelta in (False, True)
    ]
    candidatos_encontrados = [candidato for candidato in candidatos if candidato is not None]

    if not candidatos_encontrados:
        return None

    return min(candidatos_encontrados, key=lambda candidato: candidato.eta_minutos)


@enrutador.get("/me/rutas/favoritas",status_code=status.HTTP_200_OK,response_model=List[RutaFavoritaDTO])
async def obtener_rutas_favoritas(usuario: Annotated[Usuario,Depends(obtener_usuario_actual)],
                          posicion_actual_lat: float | None = None, posicion_actual_lon: float | None = None,
                          repositorio: RutasRepositorio = Depends(obtener_repositorio_rutas),
                          repositorio_buses: RepositorioBuses = Depends(obtener_repositorio_buses),
                          calculador: CalculadorGeometria = Depends(obtener_calculador_geometria)):
    caso_uso = ObtenerRutasFavoritas(repositorio)
    rutas_favoritas_encontradas = caso_uso.ejecutar(usuario.email)

    if posicion_actual_lat is None or posicion_actual_lon is None:
        return [RutaFavoritaDTO.desde_dominio(ruta) for ruta in rutas_favoritas_encontradas]

    caso_uso_bus_cercano = BuscarBusCercanoPorRuta(repositorio_buses, repositorio, calculador)

    return [
        RutaFavoritaDTO.desde_dominio(
            ruta,
            await _bus_cercano_para_favorita(caso_uso_bus_cercano, ruta, posicion_actual_lat, posicion_actual_lon),
        )
        for ruta in rutas_favoritas_encontradas
    ]

@enrutador.put("/me/rutas/favoritas/{ruta_id}",
               status_code=status.HTTP_200_OK,
               responses={
                   409:{
                       "model": ErrorResponse,
                       "description":"Ruta ya marcada como favorita"
                   }
               })
async def agregar_ruta_favorita(usuario: Annotated[Usuario,Depends(obtener_usuario_actual)],
                                ruta_id:int, repositorio: RutasRepositorio = Depends(obtener_repositorio_rutas)):
    caso_uso = AgregarRutaFavorita(repositorio)
    try:
        caso_uso.ejecutar(usuario,ruta_id)
        return {"detail": "Ruta marcada como favorita exitosamente"}
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="La ruta ya fue marcada como favorita")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"No se pudo marcar la ruta como favorita: {ex}")


@enrutador.delete("/me/rutas/favoritas/{ruta_id}",status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_ruta_favorita(usuario: Annotated[Usuario,Depends(obtener_usuario_actual)],
                                 ruta_id: int, repositorio: RutasRepositorio = Depends(obtener_repositorio_rutas)):
    caso_uso = EliminarRutaFavorita(repositorio)
    caso_uso.ejecutar(usuario,ruta_id)
