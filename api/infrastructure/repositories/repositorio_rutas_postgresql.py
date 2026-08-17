from typing import cast

import httpx
import polyline
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, cast as sa_cast, insert, delete, and_

from domain.entities.ruta import Ruta as RutaDominio
from domain.entities.busqueda_ruta import BusquedaRuta
from domain.entities.caminata import Caminata
from domain.entities.models import Coordenada
from domain.repositories.repositorio_rutas import RutasRepositorio
from infrastructure.models.osrm_ruta import OsrmRutaRespuesta
from infrastructure.models.ruta import Ruta, rutas_favoritas
from infrastructure.models.usuario import Usuario
from infrastructure.configuracion import configuracion
from geoalchemy2.functions import ST_DWithin, ST_Point, ST_SetSRID

from domain.entities.usuario import Usuario as UsuarioDominio

_osrm_client = httpx.AsyncClient(timeout=5.0)


class RutasRepositorioPostgreSql(RutasRepositorio):
    def __init__(self,db: Session):
        self.db = db

    @staticmethod
    def _a_dominio(ruta: Ruta) -> RutaDominio:
        recorrido = [
            [Coordenada(lon=lon, lat=lat) for lon, lat in linea.coords]
            for linea in to_shape(ruta.recorrido).geoms
        ]
        return RutaDominio(
            id=ruta.id,
            empresa_id=ruta.empresa_id,
            empresa_nombre=ruta.empresa.nombre,
            distancia_km=ruta.distancia_km,
            recorrido=recorrido,
            codigo=ruta.codigo,
            paradero_inicio_id=ruta.paradero_inicio_id,
            paradero_inicio_nombre=ruta.paradero_inicio.nombre,
            paradero_final_id=ruta.paradero_final.id,
            paradero_final_nombre=ruta.paradero_final.nombre,
        )


    def buscar_cercana(self, busqueda:BusquedaRuta) -> list[RutaDominio]:
        stmt = (select(Ruta)
                .options(joinedload(Ruta.empresa), joinedload(Ruta.paradero_inicio), joinedload(Ruta.paradero_final))
                .where(ST_DWithin(
            sa_cast(Ruta.recorrido,Geography),
                 sa_cast(ST_SetSRID(ST_Point(busqueda.origen.lon,busqueda.origen.lat),4326),Geography),
                 busqueda.distancia_caminata),
                ST_DWithin(sa_cast(Ruta.recorrido,Geography),
                sa_cast(ST_SetSRID(ST_Point(busqueda.destino.lon,busqueda.destino.lat),4326),Geography),
                busqueda.distancia_caminata),
                )
                .order_by(Ruta.distancia_km))
        rutas = cast(list[Ruta],self.db.scalars(stmt).all())
        return [self._a_dominio(ruta) for ruta in rutas]

    def obtener_ruta_por_codigo(self,codigo:str) -> Ruta | None:
        stmt = select(Ruta).where(Ruta.codigo == codigo)
        ruta = self.db.scalar(stmt)
        return self._a_dominio(ruta) if ruta is not None else None

    @staticmethod
    def _a_caminata(respuesta: OsrmRutaRespuesta) -> Caminata | None:
        if not respuesta.routes:
            return None
        ruta = respuesta.routes[0]
        recorrido = [Coordenada(lat=lat, lon=lon) for lat, lon in polyline.decode(ruta.geometry)]
        return Caminata(
            recorrido=recorrido,
            peso=ruta.weight,
            duracion=int(ruta.duration),
            distancia=ruta.distance,
        )

    async def calcular_caminata(self, punto_origen:Coordenada, punto_destino:Coordenada) -> Caminata | None:
        osrm_host = configuracion.osrm_host
        if not osrm_host.startswith(("http://", "https://")):
            osrm_host = f"http://{osrm_host}"
        url = f"{osrm_host}/route/v1/foot/{punto_origen.lon},{punto_origen.lat};{punto_destino.lon},{punto_destino.lat}"
        try:
            api_solicitud = await _osrm_client.get(url)
        except httpx.TransportError:
            return None
        if api_solicitud.status_code != 200:
            return None
        respuesta = OsrmRutaRespuesta.model_validate(api_solicitud.json())
        return self._a_caminata(respuesta)

    def obtener_rutas_favoritas(self, email: str) -> list[RutaDominio]:
        stmt = (select(Ruta)
                .options(joinedload(Ruta.empresa), joinedload(Ruta.paradero_inicio), joinedload(Ruta.paradero_final))
                .join(rutas_favoritas, Ruta.id == rutas_favoritas.c.ruta_id)
                .join(Usuario, rutas_favoritas.c.usuario_id == Usuario.id)
                .where(Usuario.email == email))
        rutas = cast(list[Ruta], self.db.scalars(stmt).all())
        return [self._a_dominio(ruta) for ruta in rutas]

    def agregar_ruta_favorita(self,usuario:UsuarioDominio,ruta:int):
        stmt = insert(rutas_favoritas).values(
            ruta_id=ruta,
            usuario_id=usuario.id
        )
        self.db.execute(stmt)
        self.db.commit()

    def eliminar_ruta_favorita(self,usuario:Usuario,ruta:int):
        stmt = (delete(rutas_favoritas)
                .where(and_(rutas_favoritas.c.usuario_id == usuario.id,
                            rutas_favoritas.c.ruta_id == ruta)))
        self.db.execute(stmt)
        self.db.commit()
