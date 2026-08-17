from pydantic import BaseModel

class Location(BaseModel):
    latitude: float
    longitude: float

class PlacesIDSearchResponse(BaseModel):
    id: str
    location: Location
