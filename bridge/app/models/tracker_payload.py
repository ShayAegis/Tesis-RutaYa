from datetime import datetime
from dataclasses import dataclass

from app.models.tracking_information import TrackingInformation, BusMetadata, Position


@dataclass(frozen=True)
class TrackerPayload:
    serial: str
    placa: str
    empresa_id: int
    ruta_codigo: str
    numero_bus: int
    velocidad: float
    rssi: float
    azimut: float
    timestamp: datetime
    lon: float
    lat: float
    es_vuelta: bool

    def to_tracker_information(self,mqtt_topic:str):
        return TrackingInformation(
            metadata=BusMetadata(
                rastreador_serial=self.serial,
                placa=self.placa,
                empresa_id=self.empresa_id,
                ruta_codigo=self.ruta_codigo,
                numero_bus=self.numero_bus,
            ),
            velocidad=self.velocidad,
            azimut=self.azimut,
            rssi=self.rssi,
            timestamp=self.timestamp,
            position=Position(
                lat=self.lat,
                lon=self.lon
            ),
            es_vuelta=self.es_vuelta,
            mqtt_topic=mqtt_topic
        )