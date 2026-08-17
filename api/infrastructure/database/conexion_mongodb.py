from typing import Any, Mapping

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from infrastructure.configuracion import configuracion

URL_MONGO = (f"mongodb://{configuracion.mongodb_user}:"
             f"{configuracion.mongodb_password}@{configuracion.mongodb_host}:"
             f"{configuracion.mongodb_port}")


CLIENTE_MONGO = AsyncIOMotorClient(URL_MONGO)

bd = CLIENTE_MONGO[configuracion.mongodb_name]

def obtener_coleccion() -> AsyncIOMotorCollection[Mapping[str, Any]]:
    return bd["bus_positions_history"]
