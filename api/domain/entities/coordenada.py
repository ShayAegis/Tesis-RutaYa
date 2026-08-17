from pydantic import BaseModel


class Coordenada(BaseModel):
    lat: float
    lon: float
