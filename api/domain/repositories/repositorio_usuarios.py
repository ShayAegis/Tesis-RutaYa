from datetime import datetime
from abc import ABC, abstractmethod

from domain.entities.usuario import Usuario

class RepositorioUsuarios(ABC):
    @abstractmethod
    def usuario_existe(self,email:str) -> bool:
        pass
    @abstractmethod
    def obtener_usuario_por_correo(self,email:str) -> Usuario | None:
        pass
    @abstractmethod
    def crear_usuario(self,usuario:Usuario):
        pass
    @abstractmethod
    def actualizar_ultimo_login(self,email:str):
        pass
    @abstractmethod
    def guardar_token_refresco(self,usuario: Usuario, token_hash: str,expiration: datetime):
        pass
    @abstractmethod
    def usar_token_refresco(self, token_hash: str) -> Usuario | None:
        pass