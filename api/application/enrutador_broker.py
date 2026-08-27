from fastapi import APIRouter, Depends, Header, HTTPException, status

from application.dto.rastreadores_dto import BrokerAuthDTO, BrokerAuthResultDTO
from domain.exceptions.rastreador_excepcion import SecretoRastreadorInvalidoError
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores
from domain.servicios.verificador_secreto_rastreador import VerificadorSecretoRastreador
from infrastructure.configuracion import configuracion
from infrastructure.dependencias import obtener_repositorio_rastreadores

enrutador = APIRouter(prefix="/broker", tags=["broker"])


def verificar_llave_broker(broker_key: str | None = Header(default=None, alias="Broker-Key")) -> None:
    if broker_key is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Llave de Broker no enviada")
    if broker_key != configuracion.broker_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Llave de Broker inválida")


@enrutador.post("/auth", status_code=status.HTTP_200_OK, response_model=BrokerAuthResultDTO)
async def auth(
    datos: BrokerAuthDTO,
    repositorio: RepositorioRastreadores = Depends(obtener_repositorio_rastreadores),
    _: None = Depends(verificar_llave_broker),
):
    verificador = VerificadorSecretoRastreador(repositorio)
    try:
        verificador.verificar(datos.serial, datos.secreto)
    except SecretoRastreadorInvalidoError:
        return BrokerAuthResultDTO(result="deny")
    return BrokerAuthResultDTO(result="allow")
