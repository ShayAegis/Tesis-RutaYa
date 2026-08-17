from pydantic import BaseModel


class OsrmPaso(BaseModel):
    pass

class OsrmLeg(BaseModel):
    steps: list[OsrmPaso]
    weight: float
    summary: str
    duration: float
    distance: float

class OsrmRuta(BaseModel):
    legs: list[OsrmLeg]
    weight_name: str
    geometry: str
    weight: float
    duration: float
    distance: float

class OsrmWaypoint(BaseModel):
    hint: str
    location: list[float]
    name: str
    distance: float

class OsrmRutaRespuesta(BaseModel):
    code: str
    routes: list[OsrmRuta]
    waypoints: list[OsrmWaypoint]
