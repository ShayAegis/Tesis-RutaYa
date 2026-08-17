from pydantic import BaseModel

from domain.repositories.repositorio_rastreadores import EstadoOperativoRastreador


class ParaderoDTO(BaseModel):
    lat: float
    lon: float


class EstadoRastreadorDTO(BaseModel):
    numero_bus: int
    empresa_id: int
    ruta: str
    paradero_inicio: ParaderoDTO | None
    paradero_final: ParaderoDTO | None

    @classmethod
    def desde_dominio(cls, estado: EstadoOperativoRastreador) -> "EstadoRastreadorDTO":
        return cls(
            numero_bus=estado.numero_bus,
            empresa_id=estado.empresa_id,
            ruta=estado.ruta_codigo,
            paradero_inicio=ParaderoDTO(**estado.paradero_inicio.model_dump()),
            paradero_final=ParaderoDTO(**estado.paradero_final.model_dump()),
        )
