import logging
from datetime import date, datetime, time
from datetime import timezone as dt_timezone
from typing import List, Union

from django.utils import timezone
from pymongo.errors import PyMongoError

from RutaYa.mongo import get_bus_positions_collection

logger = logging.getLogger(__name__)


def ultimas_ubicaciones_hoy(numeros_buses:Union[List[int],int]):
    """Devuelve la última ubicación reportada hoy para cada placa en `placas`."""
    if isinstance(numeros_buses,int):
        numeros_buses=[numeros_buses]

    if numeros_buses is None:
        return []

    numeros_buses = list(numeros_buses)

    inicio_dia = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        collection = get_bus_positions_collection()
        pipeline = [
            {"$match": {"metadata.numero_bus": {"$in": numeros_buses}, "timestamp": {"$gte": inicio_dia}}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$metadata.numero_bus",
                "location": {"$first": "$location"},
                "azimut": {"$first": "$azimut"},
                "timestamp": {"$first": "$timestamp"},
            }},
        ]
        return [
            {
                "numeroBus": doc["_id"],
                "lat": doc["location"]["coordinates"][1],
                "lon": doc["location"]["coordinates"][0],
                "azimut": doc["azimut"],
                "timestamp": doc["timestamp"].replace(tzinfo=dt_timezone.utc).isoformat(),
            }
            for doc in collection.aggregate(pipeline)
        ]
    except PyMongoError:
        logger.exception("no se pudo consultar bus_positions en Mongo")
        return []


def historial_ubicaciones_dia(placa: str, fecha: date) -> list[dict]:
    """Devuelve las ubicaciones reportadas por un bus (identificado por placa) en una fecha puntual."""
    inicio_dia = datetime.combine(fecha, time.min, tzinfo=dt_timezone.utc)
    fin_dia = datetime.combine(fecha, time.max, tzinfo=dt_timezone.utc)

    try:
        collection = get_bus_positions_collection()
        cursor = collection.find(
            {
                "metadata.placa": placa,
                "timestamp": {"$gte": inicio_dia, "$lte": fin_dia},
            },
            {"_id": 0, "location": 1, "timestamp": 1, "velocidad": 1},
        ).sort("timestamp", 1)

        return [
            {
                "lat": doc["location"]["coordinates"][1],
                "lng": doc["location"]["coordinates"][0],
                "velocidad": doc.get("velocidad"),
                "timestamp": doc["timestamp"].replace(tzinfo=dt_timezone.utc).isoformat(),
            }
            for doc in cursor
        ]
    except PyMongoError:
        logger.exception("no se pudo consultar el historico de ubicaciones en Mongo")
        return []
