from dataclasses import dataclass


@dataclass(frozen=True)
class TopicFields:
    empresa_id: int
    ruta_codigo: str
    numero_bus: int
