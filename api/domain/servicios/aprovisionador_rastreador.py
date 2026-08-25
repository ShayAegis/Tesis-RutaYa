import secrets

import bcrypt

from domain.exceptions.rastreador_excepcion import (
    CredencialesRastreadorIncorrectasError,
    RastreadorNoExisteError,
    RastreadorYaRegistradoError,
)
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores

LONGITUD_SECRETO_BYTES = 32


class AprovisionadorRastreador:
    def __init__(self, repositorio: RepositorioRastreadores):
        self.repositorio = repositorio

    def aprovisionar(self, serial_rastreador: str, imei_rastreador: str) -> str:
        self._validar_identidad(serial_rastreador, imei_rastreador)
        if self.repositorio.verificar_rastreador_registrado(serial_rastreador):
            raise RastreadorYaRegistradoError()
        secreto = self._generar_secreto()
        self.repositorio.registrar_secreto(serial_rastreador, self._hashear(secreto))
        return secreto

    def _validar_identidad(self, serial_rastreador: str, imei_rastreador: str) -> None:
        rastreador = self.repositorio.obtener_rastreador_por_serial(serial_rastreador)
        if rastreador is None:
            raise RastreadorNoExisteError()
        if rastreador.imei != imei_rastreador:
            raise CredencialesRastreadorIncorrectasError()

    def _generar_secreto(self) -> str:
        return secrets.token_urlsafe(LONGITUD_SECRETO_BYTES)

    def _hashear(self, secreto: str) -> str:
        return bcrypt.hashpw(secreto.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
