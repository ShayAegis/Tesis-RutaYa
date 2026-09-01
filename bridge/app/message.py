"""Parsing and validation of incoming bus-position MQTT payloads."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app import config
from app.models.tracker_payload import TrackerPayload
from app.models.topic_fields import TopicFields

class InvalidMessage(ValueError):
    """Raised when an MQTT payload does not match the expected schema."""


TOPIC_PREFIX = config.MQTT_BASETOPIC

_REQUIRED_FIELDS = (
    "lat",
    "lon",
    "azimut",
    "velocidad",
    "timestamp",
    "seq",
    "rssi",
    "esVuelta",
    "serial",
)

_TYPES: dict[str, tuple[type, ...]] = {
    "lat": (int, float),
    "lon": (int, float),
    "azimut": (int, float),
    "velocidad": (int, float),
    "timestamp": (int, float),
    "seq": (int, float),
    "rssi": (int, float),
    "esVuelta": (bool,),
    "serial": (str,),
}


def _reject_invalid_types(raw: dict[str, Any]) -> None:
    for field, expected in _TYPES.items():
        value = raw[field]
        if isinstance(value, bool) and bool not in expected:
            raise InvalidMessage(
                f"campo '{field}' tiene tipo invalido: {type(value).__name__}"
            )
        if not isinstance(value, expected):
            raise InvalidMessage(
                f"campo '{field}' tiene tipo invalido: {type(value).__name__}"
            )


def _reject_out_of_range(lat: float, lon: float) -> None:
    if not (-90 <= lat <= 90):
        raise InvalidMessage(f"lat fuera de rango: {lat}")
    if not (-180 <= lon <= 180):
        raise InvalidMessage(f"lon fuera de rango: {lon}")


def parse_topic(topic: str) -> TopicFields:
    """Extract empresa_id, ruta_codigo y numero_bus del tópico MQTT.
    Estructura esperada: buses/{empresa_id}/{ruta_codigo}/{numero_bus}
    Raises InvalidMessage si el tópico no coincide con esa estructura.
    """
    parts = topic.split("/")
    if len(parts) != 4 or parts[0] != TOPIC_PREFIX:
        raise InvalidMessage(f"topico con formato invalido: '{topic}'")

    _, empresa_id, ruta_codigo, numero_bus = parts
    if not empresa_id.isdigit() or not numero_bus.isdigit() or not ruta_codigo:
        raise InvalidMessage(f"topico con formato invalido: '{topic}'")

    return TopicFields(
        empresa_id=int(empresa_id),
        ruta_codigo=ruta_codigo,
        numero_bus=int(numero_bus),
    )


def parse_payload(raw: dict[str, Any], topic: TopicFields) -> TrackerPayload:
    """Validate raw dict and build a Position.
    Raises InvalidMessage if a required field is missing or has the wrong type.
    """
    missing = [field for field in _REQUIRED_FIELDS if field not in raw]
    if missing:
        raise InvalidMessage(f"campos faltantes: {', '.join(missing)}")

    _reject_invalid_types(raw)

    lat = float(raw["lat"])
    lon = float(raw["lon"])
    _reject_out_of_range(lat, lon)

    return TrackerPayload(
        serial=raw["serial"],
        placa=raw["placa"],
        empresa_id=topic.empresa_id,
        ruta_codigo=topic.ruta_codigo,
        numero_bus=topic.numero_bus,
        azimut=raw["azimut"],
        velocidad=float(raw["velocidad"]),
        rssi=float(raw["rssi"]),
        timestamp=datetime.fromtimestamp(raw["timestamp"], tz=timezone.utc),
        lon=lon,
        lat=lat,
        es_vuelta=raw["esVuelta"],
        seq=int(raw["seq"])
    )
