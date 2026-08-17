from pydantic import BaseModel

from domain.entities.coordenada import Coordenada


class Ruta(BaseModel):
    id: int
    empresa_id: int
    empresa_nombre: str
    distancia_km: float
    recorrido: list[list[Coordenada]]
    codigo: str
    paradero_inicio_id: int
    paradero_inicio_nombre: str
    paradero_final_id: int
    paradero_final_nombre: str