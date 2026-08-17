from motor.motor_asyncio import AsyncIOMotorCollection
from sqlalchemy.orm import Session
from fastapi import Depends
from redis import Redis

from domain.repositories.repositorio_buses import RepositorioBuses
from domain.repositories.repositorio_lugares import RepositorioLugares
from domain.repositories.repositorio_rutas import RutasRepositorio
from domain.repositories.repositorio_transmision_ubicacion_bus import RepositorioTransmisionUbicacionBus
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores
from domain.repositories.repositorio_usuarios import RepositorioUsuarios
from domain.servicios.calculador_geometria import CalculadorGeometria
from infrastructure.database.conexion_postgis import obtener_sesion_bd
from infrastructure.database.conexion_redis import obtener_conexion_redis, obtener_conexion_redis_async
from infrastructure.repositories.repositorio_buses_mongodb import RepositorioBusesMongodb
from infrastructure.repositories.repositorio_transmision_ubicacion_bus_redis import RepositorioTransmisionUbicacionRedis
from infrastructure.repositories.repositorio_rastreadores_postgresql import RepositorioRastreadoresPostgreSql
from infrastructure.repositories.repositorio_rutas_postgresql import RutasRepositorioPostgreSql
from infrastructure.repositories.repositorio_usuarios_postgresql import RepositorioUsuariosPostgreSql
from infrastructure.repositories.repositorio_lugares_api_google import RepositorioLugaresAPIGoogle
from infrastructure.database.conexion_mongodb import obtener_coleccion
from infrastructure.services.shapely_calculador_geometria import ShapelyCalculadorGeometria


def obtener_repositorio_rastreadores(db: Session = Depends(obtener_sesion_bd)) -> RepositorioRastreadores:
    return RepositorioRastreadoresPostgreSql(db)

def obtener_repositorio_buses(db: AsyncIOMotorCollection = Depends(obtener_coleccion)) -> RepositorioBuses:
    return RepositorioBusesMongodb(db)

def obtener_repositorio_transmision_ubicacion_bus() -> RepositorioTransmisionUbicacionBus:
    return RepositorioTransmisionUbicacionRedis(obtener_conexion_redis_async())

def obtener_repositorio_rutas(db: Session = Depends(obtener_sesion_bd)) -> RutasRepositorio:
    return RutasRepositorioPostgreSql(db)

def obtener_repositorio_usuarios(db: Session = Depends(obtener_sesion_bd)) -> RepositorioUsuarios:
    return RepositorioUsuariosPostgreSql(db)

def obtener_repositorio_lugares(db: Redis = Depends(obtener_conexion_redis)) -> RepositorioLugares:
    return RepositorioLugaresAPIGoogle(db)

def obtener_calculador_geometria() -> CalculadorGeometria:
    return ShapelyCalculadorGeometria()