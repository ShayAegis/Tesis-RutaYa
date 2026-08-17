from fastapi import APIRouter, Depends, Header,status, HTTPException

from application.dto.rastreadores_dto import EstadoRastreadorDTO
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores
from domain.usecase.obtener_informacion_bus import ObtenerInformacionBus
from infrastructure.dependencias import obtener_repositorio_rastreadores

from typing import Annotated

enrutador = APIRouter(prefix="/rastreadores", tags=["rastreadores"])


@enrutador.get("/me",status_code=status.HTTP_200_OK,response_model=EstadoRastreadorDTO)
async def estado_rastreador(serial_id: Annotated[str | None,Header(alias="Rastreador-Serial")]=None,
              repositorio: RepositorioRastreadores = Depends(obtener_repositorio_rastreadores)):
    if not serial_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Serial del rastreador no enviado")
    caso_uso = ObtenerInformacionBus(repositorio)
    estado_bus = caso_uso.ejecutar(serial_id)
    if estado_bus is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No se encontró un bus asociado al rastreador")
    return EstadoRastreadorDTO.desde_dominio(estado_bus)
