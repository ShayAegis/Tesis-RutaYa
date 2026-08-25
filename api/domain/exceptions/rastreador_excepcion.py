class RastreadorNoExisteError(Exception):
    def __init__(self):
        super().__init__("El rastreador no existe")


class CredencialesRastreadorIncorrectasError(Exception):
    def __init__(self):
        super().__init__("Las credenciales del rastreador son incorrectas")


class RastreadorYaRegistradoError(Exception):
    def __init__(self):
        super().__init__("El rastreador ya se encuentra registrado")


class SecretoRastreadorInvalidoError(Exception):
    def __init__(self):
        super().__init__("El secreto del rastreador es inválido")
