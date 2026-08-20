from collections.abc import AsyncIterator

from domain.repositories.repositorio_transmision_ubicacion_bus import RepositorioTransmisionUbicacionBus


class FakeRepositorioTransmisionUbicacionBus(RepositorioTransmisionUbicacionBus):
    """Repositorio en memoria para no depender de Redis/MQTT en los tests.

    A diferencia de un pub/sub real, el fake emite un número fijo de mensajes
    y termina, para que el test no se quede esperando indefinidamente.
    """

    def __init__(self, mensajes: list[bytes]):
        self.mensajes = mensajes
        self.temas_recibidos: list[str] = []

    async def suscribir(self, tema: str) -> AsyncIterator[bytes]:
        self.temas_recibidos.append(tema)
        for mensaje in self.mensajes:
            yield mensaje
