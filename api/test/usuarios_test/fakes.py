from datetime import datetime

from domain.entities.usuario import Usuario
from domain.repositories.repositorio_usuarios import RepositorioUsuarios


class FakeRepositorioUsuarios(RepositorioUsuarios):
    """Repositorio en memoria para no depender de la base de datos en los tests."""

    def __init__(self, usuarios: list[Usuario] | None = None):
        self._usuarios = usuarios or []

    def usuario_existe(self, email: str) -> bool:
        return any(usuario.email == email for usuario in self._usuarios)

    def obtener_usuario_por_correo(self, email: str) -> Usuario | None:
        return next((usuario for usuario in self._usuarios if usuario.email == email), None)

    def crear_usuario(self, usuario: Usuario):
        nuevo_usuario = usuario.model_copy(update={"id": len(self._usuarios) + 1})
        self._usuarios.append(nuevo_usuario)

    def actualizar_ultimo_login(self, email: str):
        pass

    def guardar_token_refresco(self, usuario: Usuario, token_hash: str, expiration: datetime):
        pass

    def usar_token_refresco(self, token_hash: str) -> Usuario | None:
        return None
