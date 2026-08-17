from abc import ABC, abstractmethod
from typing import AsyncIterator


class RepositorioTransmisionUbicacionBus(ABC):
    @abstractmethod
    def suscribir(self, tema: str) -> AsyncIterator[bytes]:
        pass
