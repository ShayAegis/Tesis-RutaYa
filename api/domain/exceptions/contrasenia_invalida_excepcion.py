class ContraseniaInvalidaError(Exception):
    pass


class ContraseniaMuyCortaError(ContraseniaInvalidaError):
    LONGITUD_MINIMA = 8

    def __init__(self):
        super().__init__(f"La contraseña debe tener al menos {self.LONGITUD_MINIMA} caracteres")


class ContraseniaSecuenciaNumericaError(ContraseniaInvalidaError):
    def __init__(self):
        super().__init__("La contraseña no puede ser una secuencia numérica simple (ej. 123456789)")


class ContraseniaSinLetrasYNumerosError(ContraseniaInvalidaError):
    def __init__(self):
        super().__init__("La contraseña debe contener al menos una letra y un número")
