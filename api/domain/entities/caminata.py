from pydantic import BaseModel

from domain.entities.coordenada import Coordenada


class Caminata(BaseModel):
    recorrido: list[Coordenada]
    peso: int | float
    duracion: int
    distancia: float