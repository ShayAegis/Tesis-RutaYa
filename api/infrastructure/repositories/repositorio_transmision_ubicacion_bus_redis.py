import json
from typing import AsyncIterator

from redis.asyncio import Redis

from domain.repositories.repositorio_transmision_ubicacion_bus import RepositorioTransmisionUbicacionBus

ESTADO_BUSES_KEY = "buses:state"


class RepositorioTransmisionUbicacionRedis(RepositorioTransmisionUbicacionBus):
    def __init__(self, redis: Redis):
        self._redis = redis

    async def _buscar_estado_actual(self, tema: str) -> str | None:
        numero_bus = int(tema.rsplit("/", 1)[-1])
        estados = await self._redis.hgetall(ESTADO_BUSES_KEY)
        for estado_json in estados.values():
            if json.loads(estado_json).get("numero_bus") == numero_bus:
                return estado_json
        return None

    async def suscribir(self, tema: str) -> AsyncIterator[bytes]:
        pubsub = self._redis.pubsub()
        try:
            await pubsub.subscribe(tema)
            estado_actual = await self._buscar_estado_actual(tema)
            if estado_actual is not None:
                yield estado_actual
            async for mensaje in pubsub.listen():
                if mensaje["type"] == "message":
                    yield mensaje["data"]
        finally:
            await pubsub.unsubscribe(tema)
            await pubsub.close()
