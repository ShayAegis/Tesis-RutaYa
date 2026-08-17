from typing import Optional

from pydantic import BaseModel

from domain.entities.coordenada import Coordenada

class SugerenciaLugar(BaseModel):
    id: str
    nombre_lugar: str
    ubicacion: Coordenada
    coincidencia_hasta_indice: Optional[int] = None