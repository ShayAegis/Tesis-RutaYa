from pydantic.dataclasses import dataclass

from domain.entities.pierna import Pierna

@dataclass
class Itinerario:
    piernas: list[Pierna]

    @property
    def distancia(self) -> float:
        return sum(p.distancia for p in self.piernas)

    @property
    def eta(self) -> float:
        return sum(p.duracion for p in self.piernas)

    @property
    def peso(self) -> float:
        return sum(p.peso for p in self.piernas)

    @property
    def numero_transbordos(self) -> int:
        return sum(1 for p in self.piernas if p.perfil == "bus") - 1
