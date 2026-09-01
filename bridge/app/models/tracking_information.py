from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class Position:
    lon: float
    lat: float

@dataclass(frozen=True)
class BusMetadata:
    rastreador_serial: str
    placa: str
    empresa_id: int
    ruta_codigo: str
    numero_bus: int

@dataclass(frozen=True)
class TrackingInformation:
    metadata: BusMetadata
    velocidad: float
    rssi: float
    timestamp: datetime
    position: Position
    azimut: float
    es_vuelta: bool
    mqtt_topic:str
    seq: int

    @property
    def bus_id(self) -> str:
        return self.metadata.placa or self.metadata.rastreador_serial

    def dump_json(self) -> dict[str,Any]:

        return {
        "metadata": {
            "placa": self.metadata.placa,
            "empresa_id": self.metadata.empresa_id,
            "ruta_codigo": self.metadata.ruta_codigo,
            "numero_bus": self.metadata.numero_bus,
            "serial_rastreador": self.metadata.rastreador_serial
        },
        "velocidad": self.velocidad,
        "azimut": self.azimut,
        "es_vuelta": self.es_vuelta,
        "timestamp": self.timestamp,
        "location": {
            "type": "Point",
            "coordinates": [self.position.lon, self.position.lat],
        },
        "received_at": datetime.now(timezone.utc),
        "topic": self.mqtt_topic,
        "seq": self.seq,
        }