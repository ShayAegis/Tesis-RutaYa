from domain.repositories.repositorio_rastreadores import RepositorioRastreadores, EstadoOperativoRastreador


class ObtenerInformacionBus:
    def __init__(self, repositorio: RepositorioRastreadores):
        self.repositorio = repositorio

    def ejecutar(self, serial: str) -> EstadoOperativoRastreador | None:
        estado_rastreador = self.repositorio.obtener_estado_operativo(serial)
        if estado_rastreador is None:
            return None
        return estado_rastreador
