from pydantic import BaseModel

from domain.entities.ruta import Ruta


class RutaEncontrada(BaseModel):
    ruta: Ruta
    retorno: bool
