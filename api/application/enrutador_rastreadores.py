from fastapi import APIRouter, Depends, Header,status, HTTPException
from application.dto.rastreadores_dto import RastreadorRegistroInfo, RastreadorSecretoDTO
from application.dto.rastreadores_dto import EstadoRastreadorDTO
from domain.exceptions.rastreador_excepcion import (
    RastreadorNoExisteError,
    CredencialesRastreadorIncorrectasError,
    RastreadorYaRegistradoError,
    SecretoRastreadorInvalidoError,
)
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores
from domain.servicios.aprovisionador_rastreador import AprovisionadorRastreador
from domain.servicios.verificador_secreto_rastreador import VerificadorSecretoRastreador
from domain.usecase.obtener_informacion_bus import ObtenerInformacionBus
from infrastructure.dependencias import obtener_repositorio_rastreadores

from typing import Annotated

enrutador = APIRouter(prefix="/rastreadores", tags=["rastreadores"])


@enrutador.post("/aprovisionar",status_code=status.HTTP_200_OK,response_model=RastreadorSecretoDTO)
async def aprovisionar(rastreador_info: RastreadorRegistroInfo, repositorio:RepositorioRastreadores = Depends(obtener_repositorio_rastreadores)):
    aprovisionador = AprovisionadorRastreador(repositorio)
    try:
        secreto = aprovisionador.aprovisionar(rastreador_info.serial,rastreador_info.imei)
        return RastreadorSecretoDTO(secreto=secreto)
    except RastreadorNoExisteError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="El rastreador no existe")
    except CredencialesRastreadorIncorrectasError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Las credenciales del rastreado son incorrectas")
    except RastreadorYaRegistradoError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Rastreador ya registrado")

@enrutador.get("/me",status_code=status.HTTP_200_OK,response_model=EstadoRastreadorDTO)
async def estado_rastreador(secreto_rastreador: Annotated[str | None,Header(alias="Rastreador-Secreto")]=None,
                serial_id:str | None =  None, repositorio: RepositorioRastreadores = Depends(obtener_repositorio_rastreadores)):
    if not secreto_rastreador:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Secreto del rastreador no enviado")
    if not serial_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Serial del rastreador no enviado")
    verificador = VerificadorSecretoRastreador(repositorio)
    try:
        verificador.verificar(serial_id, secreto_rastreador)
    except SecretoRastreadorInvalidoError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Secreto del rastreador inválido")
    caso_uso = ObtenerInformacionBus(repositorio)
    estado_bus = caso_uso.ejecutar(serial_id)
    if estado_bus is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontró un bus asociado al rastreador")
    return EstadoRastreadorDTO.desde_dominio(estado_bus)
