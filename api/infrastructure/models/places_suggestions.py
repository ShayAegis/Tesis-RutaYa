from pydantic import BaseModel

class TextMatch(BaseModel):
    endOffset: int | None = None

class Text(BaseModel):
    text: str
    matches: list[TextMatch]

class PlacePrediction(BaseModel):
    placeId: str
    text: Text

class Suggestion(BaseModel):
    placePrediction: PlacePrediction

class PlacesAPIResponse(BaseModel):
    suggestions: list[Suggestion]