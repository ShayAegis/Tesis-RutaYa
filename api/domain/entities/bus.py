from pydantic import BaseModel

from domain.entities.coordenada import Coordenada


class Bus(BaseModel):
    placa: str
    numero_bus: int
    empresa_id: int
    ultima_ubicacion: Coordenada | None = None
