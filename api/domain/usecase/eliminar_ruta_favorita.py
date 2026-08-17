from domain.entities.usuario import Usuario
from domain.repositories.repositorio_rutas import RutasRepositorio


class EliminarRutaFavorita:
    def __init__(self,repositorio: RutasRepositorio):
        self.repositorio = repositorio
    def ejecutar(self,usuario:Usuario,ruta_id:int):
        self.repositorio.eliminar_ruta_favorita(usuario,ruta_id)
