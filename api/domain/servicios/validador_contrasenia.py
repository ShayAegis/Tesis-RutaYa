from abc import ABC, abstractmethod

from domain.exceptions.contrasenia_invalida_excepcion import (
    ContraseniaMuyCortaError,
    ContraseniaSecuenciaNumericaError,
    ContraseniaSinLetrasYNumerosError,
)

SECUENCIAS_NUMERICAS_PROHIBIDAS = {
    "0123456789"[i:j]
    for i in range(10)
    for j in range(i + 4, 11)
} | {
    "9876543210"[i:j]
    for i in range(10)
    for j in range(i + 4, 11)
}


class ValidadorContrasenia(ABC):
    _siguiente: "ValidadorContrasenia | None" = None

    def encadenar(self, siguiente: "ValidadorContrasenia") -> "ValidadorContrasenia":
        self._siguiente = siguiente
        return siguiente

    def validar(self, contrasenia: str) -> None:
        self._validar(contrasenia)
        if self._siguiente is not None:
            self._siguiente.validar(contrasenia)

    @abstractmethod
    def _validar(self, contrasenia: str) -> None:
        pass


class ValidadorLongitudMinima(ValidadorContrasenia):
    def _validar(self, contrasenia: str) -> None:
        if len(contrasenia) < ContraseniaMuyCortaError.LONGITUD_MINIMA:
            raise ContraseniaMuyCortaError()


class ValidadorSecuenciaNumerica(ValidadorContrasenia):
    def _validar(self, contrasenia: str) -> None:
        if contrasenia in SECUENCIAS_NUMERICAS_PROHIBIDAS:
            raise ContraseniaSecuenciaNumericaError()


class ValidadorLetrasYNumeros(ValidadorContrasenia):
    def _validar(self, contrasenia: str) -> None:
        tiene_letra = any(caracter.isalpha() for caracter in contrasenia)
        tiene_numero = any(caracter.isdigit() for caracter in contrasenia)
        if not (tiene_letra and tiene_numero):
            raise ContraseniaSinLetrasYNumerosError()


def crear_cadena_validacion_contrasenia() -> ValidadorContrasenia:
    longitud = ValidadorLongitudMinima()
    secuencia = ValidadorSecuenciaNumerica()
    letras_numeros = ValidadorLetrasYNumeros()

    longitud.encadenar(secuencia).encadenar(letras_numeros)
    return longitud
