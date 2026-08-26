from fastapi import APIRouter, Depends, status

from application.dto.rastreadores_dto import BrokerAuthDTO, BrokerAuthResultDTO
from domain.exceptions.rastreador_excepcion import SecretoRastreadorInvalidoError
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores
from domain.servicios.verificador_secreto_rastreador import VerificadorSecretoRastreador
from infrastructure.dependencias import obtener_repositorio_rastreadores

enrutador = APIRouter(prefix="/broker", tags=["broker"])


@enrutador.post("/auth", status_code=status.HTTP_200_OK, response_model=BrokerAuthResultDTO)
async def auth(datos: BrokerAuthDTO, repositorio: RepositorioRastreadores = Depends(obtener_repositorio_rastreadores)):
    verificador = VerificadorSecretoRastreador(repositorio)
    try:
        verificador.verificar(datos.serial, datos.secreto)
    except SecretoRastreadorInvalidoError:
        return BrokerAuthResultDTO(result="deny")
    return BrokerAuthResultDTO(result="allow")
