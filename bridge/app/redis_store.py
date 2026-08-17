"""Estado actual de cada bus en Redis, con indice geoespacial para consultas."""

import json
from typing import TYPE_CHECKING
from typing import Any
import redis

from app import config

if TYPE_CHECKING:
    from app.models.tracking_information import TrackingInformation

GEO_KEY = "buses:geo"
STATE_KEY_PREFIX = "buses:state"
BUSES_RUTAS_KEY = "buses:rutas"

def get_client() -> redis.Redis:
    return redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD,
        decode_responses=True,
    )


def save_current_state(client: redis.Redis, tracking_information: TrackingInformation, topic: str) -> None:
    metadata = tracking_information.metadata
    position = tracking_information.position
    state: dict[str,Any] = {
        "placa": metadata.placa or "",
        "empresa_id": metadata.empresa_id,
        "ruta_codigo": metadata.ruta_codigo,
        "numero_bus": metadata.numero_bus,
        "serial": metadata.rastreador_serial,
        "rssi": tracking_information.rssi,
        "velocidad": tracking_information.velocidad,
        "azimut": tracking_information.azimut,
        "lat": position.lat,
        "lon": position.lon,
        "timestamp": tracking_information.timestamp.isoformat(),
        "es_vuelta": int(tracking_information.es_vuelta),
    }
    payload = json.dumps(state)

    pipe = client.pipeline()
    pipe.hset(name=STATE_KEY_PREFIX, key=state.get("placa"), value=payload)
    pipe.hexpire(STATE_KEY_PREFIX, 30, state.get("placa"))
    pipe.publish(topic, payload)
    pipe.execute()

