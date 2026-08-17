from pydantic import BaseModel

from domain.entities.coordenada import Coordenada


class BusquedaRuta(BaseModel):
    origen: Coordenada
    destino: Coordenada
    distancia_caminata: int