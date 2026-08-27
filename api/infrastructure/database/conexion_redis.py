import logging

import redis
import redis.asyncio as redis_asyncio
from infrastructure.configuracion import configuracion

_pool_async = redis_asyncio.ConnectionPool(host=configuracion.redis_host,
                                            port=configuracion.redis_port,
                                            password=configuracion.redis_password,
                                            db=0,
                                            decode_responses=True,
                                            max_connections=configuracion.redis_max_connections)

_pool_sincrono = redis.ConnectionPool(host=configuracion.redis_host,
                                       port=configuracion.redis_port,
                                       password=configuracion.redis_password,
                                       db=configuracion.redis_db,
                                       decode_responses=True,
                                       max_connections=configuracion.redis_max_connections)

def obtener_conexion_redis_async() -> redis_asyncio.Redis:
    return redis_asyncio.Redis(connection_pool=_pool_async)

def obtener_conexion_redis():

    logger = logging.getLogger(__name__)

    redis_cliente = redis.Redis(connection_pool=_pool_sincrono)

    with redis_cliente as redis_conexion:
        try:
            redis_conexion.ping()
            logger.info("Conectado a redis")
            yield redis_conexion
        except redis.ConnectionError:
            logger.error("Hubo un problema al conectarse a Redis")
        except redis.AuthenticationError:
            logger.error("Hubo un problema al conectarse a Redis, las credenciales de conexión no son correctas")
        except redis.TimeoutError:
            logger.error("Hubo un problema al conectarse a Redis, Redis tomó mucho tiempo en responder")
