from datetime import datetime
from pydantic import BaseModel

class ActualizacionUbicacionDTO(BaseModel):
    lat: float
    lon: float
    velocidad: float
    azimut: float
    timestamp: datetime