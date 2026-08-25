import bcrypt

from domain.exceptions.rastreador_excepcion import SecretoRastreadorInvalidoError
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores


class VerificadorSecretoRastreador:
    def __init__(self, repositorio: RepositorioRastreadores):
        self.repositorio = repositorio

    def verificar(self, serial_rastreador: str, secreto: str) -> None:
        hash_guardado = self.repositorio.obtener_hash_secreto(serial_rastreador)
        if hash_guardado is None or not self._coincide(secreto, hash_guardado):
            raise SecretoRastreadorInvalidoError()

    def _coincide(self, secreto: str, hash_guardado: str) -> bool:
        try:
            return bcrypt.checkpw(secreto.encode("utf-8"), hash_guardado.encode("utf-8"))
        except ValueError:
            return False
