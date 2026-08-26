from datetime import time

from pydantic import BaseModel

from domain.repositories.repositorio_rastreadores import EstadoOperativoRastreador


class ParaderoDTO(BaseModel):
    lat: float
    lon: float

class RastreadorRegistroInfo(BaseModel):
    serial: str
    imei: str

class RastreadorSecretoDTO(BaseModel):
    secreto: str

class BrokerAuthDTO(BaseModel):
    serial: str
    secreto: str

class BrokerAuthResultDTO(BaseModel):
    result: str

class EstadoRastreadorDTO(BaseModel):
    numero_bus: int
    empresa_id: int
    ruta: str
    ruta_hora_inicio: time
    ruta_hora_fin: time
    paradero_inicio: ParaderoDTO | None
    paradero_final: ParaderoDTO | None

    @classmethod
    def desde_dominio(cls, estado: EstadoOperativoRastreador) -> "EstadoRastreadorDTO":
        return cls(
            numero_bus=estado.numero_bus,
            empresa_id=estado.empresa_id,
            ruta=estado.ruta_codigo,
            ruta_hora_inicio=estado.ruta_hora_inicio,
            ruta_hora_fin=estado.ruta_hora_fin,
            paradero_inicio=ParaderoDTO(**estado.paradero_inicio.model_dump()),
            paradero_final=ParaderoDTO(**estado.paradero_final.model_dump()),
        )
