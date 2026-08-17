from typing import List

from domain.entities.ruta import Ruta
from domain.repositories.repositorio_rutas import RutasRepositorio


class ObtenerRutasFavoritas:
    def __init__(self, repositorio: RutasRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, email: str) -> List[Ruta]:
        return self.repositorio.obtener_rutas_favoritas(email)
