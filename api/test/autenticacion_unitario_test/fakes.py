from datetime import datetime, timezone

from domain.entities.usuario import Usuario
from domain.repositories.repositorio_usuarios import RepositorioUsuarios


class FakeRepositorioUsuarios(RepositorioUsuarios):
    """Repositorio en memoria para no depender de la base de datos en los tests.

    A diferencia del fake usado en usuarios_integracion_test, este sí valida
    de verdad el token de refresco (hash + expiración), porque el test que lo
    usa necesita ejercitar el flujo real login -> refresh.
    """

    def __init__(self, usuarios: list[Usuario]):
        self._usuarios = usuarios
        self._token_refresco_hash: str | None = None
        self._token_refresco_expiracion: datetime | None = None
        self._usuario_del_token: Usuario | None = None

    def usuario_existe(self, email: str) -> bool:
        return any(usuario.email == email for usuario in self._usuarios)

    def obtener_usuario_por_correo(self, email: str) -> Usuario | None:
        return next((usuario for usuario in self._usuarios if usuario.email == email), None)

    def crear_usuario(self, usuario: Usuario):
        self._usuarios.append(usuario)

    def actualizar_ultimo_login(self, email: str):
        pass

    def guardar_token_refresco(self, usuario: Usuario, token_hash: str, expiration: datetime):
        self._token_refresco_hash = token_hash
        self._token_refresco_expiracion = expiration
        self._usuario_del_token = usuario

    def usar_token_refresco(self, token_hash: str) -> Usuario | None:
        if token_hash != self._token_refresco_hash:
            return None
        if self._token_refresco_expiracion is None or self._token_refresco_expiracion <= datetime.now(timezone.utc):
            return None
        return self._usuario_del_token
