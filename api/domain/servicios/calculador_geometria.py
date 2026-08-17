from abc import ABC, abstractmethod

from domain.entities.coordenada import Coordenada


class CalculadorGeometria(ABC):
    @abstractmethod
    def proyectar_punto_en_trayecto(self, trayecto: list[Coordenada], punto: Coordenada) -> float:
        pass

    @abstractmethod
    def subtrayecto(self, trayecto: list[Coordenada], distancia_inicio: float, distancia_fin: float) -> list[Coordenada]:
        pass

    @abstractmethod
    def simplificar(self, trayecto: list[Coordenada], tolerancia: float) -> list[Coordenada]:
        pass

    @abstractmethod
    def longitud_metros(self, trayecto: list[Coordenada]) -> float:
        pass

    @abstractmethod
    def distancia_puntos_metros(self, a: Coordenada, b: Coordenada) -> float:
        pass

    @abstractmethod
    def punto_intersecta_trayecto(self,punto: Coordenada, trayecto: list[Coordenada], buffer: float = 0) -> bool:
        pass