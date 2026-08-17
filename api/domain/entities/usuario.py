from pydantic import BaseModel

class Usuario(BaseModel):
    id: int | None
    email: str
    nombres: str
    apellidos: str
    contrasenia: str