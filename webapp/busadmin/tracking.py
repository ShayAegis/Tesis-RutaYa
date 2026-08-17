from typing import List, Union
import logging
from datetime import datetime, timedelta

import json
import redis
from django.utils import timezone

from RutaYa.redis_client import get_redis_client

logger = logging.getLogger(__name__)

STATE_KEY = "buses:state"


def getLastLocation(placas:Union[List[str] | str], ventanaMinutos:int=5) -> dict[str, float]:
    """Para las placas con estado reciente en Redis, devuelve
    un dict {busPlaca: rssi} con el rssi de su reporte más reciente."""
    if isinstance(placas,str):
        placas = [placas]

    if not placas:
        return {}

    cutoff = timezone.now() - timedelta(minutes=ventanaMinutos)

    try:
        client = get_redis_client()
        pipe = client.pipeline()
        for placa in placas:
            pipe.hget(STATE_KEY, placa)
        estados = pipe.execute()

        ubicaciones = {}
        for placa, estado_raw in zip(placas, estados):
            if not estado_raw:
                continue
            estado = json.loads(estado_raw)
            if "rssi" not in estado or "timestamp" not in estado:
                continue
            if datetime.fromisoformat(estado["timestamp"]) < cutoff:
                continue
            ubicaciones[placa] = float(estado["rssi"])
        return ubicaciones
    except redis.RedisError:
        logger.exception("no se pudo consultar el estado de buses en Redis")
        return {}


# El firmware del rastreador (SIM7000) convierte el CSQ a dBm real
# (rango aprox. -113 a -51) y usa 99 como centinela cuando no pudo leer señal.
RSSI_SIN_LECTURA = 90
RSSI_BUENA = -70
RSSI_MEDIA = -90


def getIconBySignal(rssi):
    """Devuelve el ícono FontAwesome, color Bootstrap y texto descriptivo para un rssi en dBm."""
    if rssi is None or rssi >= RSSI_SIN_LECTURA:
        return {"icono": "fa-signal", "color": "text-muted", "titulo": "Sin datos de señal"}
    if rssi >= RSSI_BUENA:
        return {"icono": "fa-signal-perfect", "color": "text-success", "titulo": f"Señal buena ({rssi:.0f} dBm)"}
    if rssi >= RSSI_MEDIA:
        return {"icono": "fa-signal", "color": "text-warning", "titulo": f"Señal media ({rssi:.0f} dBm)"}
    return {"icono": "fa-signal", "color": "text-danger", "titulo": f"Señal débil ({rssi:.0f} dBm)"}
