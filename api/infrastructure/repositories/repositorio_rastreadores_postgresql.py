from datetime import datetime, timezone, timedelta

from sqlalchemy import select, and_, exists
from sqlalchemy.orm import aliased, Session
from geoalchemy2.functions import ST_X, ST_Y

from domain.entities.models import Coordenada
from domain.entities.rastreador import Rastreador as RastreadorDominio
from domain.repositories.repositorio_rastreadores import RepositorioRastreadores, EstadoOperativoRastreador
from infrastructure.models.bus import Bus
from infrastructure.models.rastreador import AsignacionRastreador, Rastreador, SecretoRastreador
from infrastructure.models.paradero import Paradero
from infrastructure.models.ruta import AsignacionRuta, HorarioOperacion, Ruta


class RepositorioRastreadoresPostgreSql(RepositorioRastreadores):
    def __init__(self, db: Session):
        self.db = db

    def obtener_estado_operativo(self, serial: str) -> EstadoOperativoRastreador | None:

        ParaderoInicio = aliased(Paradero,name="paraderoinicio")
        ParaderoFinal = aliased(Paradero)
        dia_actual = datetime.now().weekday()
        consulta = (
            select(
                Bus.numero_bus,
                Bus.empresa_id,
                Ruta.codigo.label("ruta_codigo"),
                ST_X(ParaderoInicio.ubicacion).label("paradero_inicio_lon"),
                ST_Y(ParaderoInicio.ubicacion).label("paradero_inicio_lat"),
                ST_X(ParaderoFinal.ubicacion).label("paradero_final_lon"),
                ST_Y(ParaderoFinal.ubicacion).label("paradero_final_lat"),
                HorarioOperacion.hora_inicio,
                HorarioOperacion.hora_fin
            ).select_from(AsignacionRastreador)
            .join(Bus,AsignacionRastreador.bus_id == Bus.placa)
            .join(AsignacionRuta,Bus.placa == AsignacionRuta.bus_id)
            .join(Ruta,AsignacionRuta.ruta_id == Ruta.id)
            .join(ParaderoInicio, Ruta.paradero_inicio_id == ParaderoInicio.id)
            .join(ParaderoFinal, Ruta.paradero_final_id == ParaderoFinal.id)
            .join(HorarioOperacion, Ruta.id == HorarioOperacion.ruta_id)
            .where(
                AsignacionRastreador.rastreador_id == serial,
                AsignacionRastreador.fecha_fin.is_(None),
                AsignacionRuta.fecha_fin.is_(None),
                HorarioOperacion.dia == dia_actual
            )
        )
        resultado = self.db.execute(consulta).one_or_none()

        if resultado is None:
            return None
        
        return EstadoOperativoRastreador(
            numero_bus=resultado.numero_bus,
            empresa_id=resultado.empresa_id,
            ruta_codigo=resultado.ruta_codigo,
            ruta_hora_inicio=resultado.hora_inicio,
            ruta_hora_fin=resultado.hora_fin,
            paradero_inicio = Coordenada(lat=resultado.paradero_inicio_lat, lon=resultado.paradero_inicio_lon),
            paradero_final = Coordenada(lat=resultado.paradero_final_lat, lon=resultado.paradero_final_lon)
        )

    def obtener_rastreador_por_serial(self, serial: str) -> RastreadorDominio | None:
        consulta = (
            select(Rastreador)
            .where(
                Rastreador.serial == serial
            )
        )

        rastreador = self.db.scalar(consulta)
        if rastreador is None:
            return None

        return RastreadorDominio(
           serial = rastreador.serial,
           modelo = rastreador.modelo,
           imei = rastreador.imei,
           iccid = rastreador.iccid,
           operador_red = rastreador.operador_red.nombre,
           numero_sim = rastreador.numero_sim,
           empresa = rastreador.empresa.nombre
        )

    def verificar_rastreador_registrado(self, serial: str) -> bool:
        consulta = select(
            exists().where(SecretoRastreador.rastreador_serial == serial)
        )

        return bool(self.db.scalar(consulta))

    def registrar_secreto(self, serial: str, secreto_hasheado: str) -> None:
        secreto = SecretoRastreador(
            rastreador_serial=serial,
            secreto_hash=secreto_hasheado,
            issued_at=datetime.now(timezone(timedelta(hours=-5)))
        )
        self.db.add(secreto)
        self.db.commit()

    def obtener_hash_secreto(self, serial: str) -> str | None:
        consulta = select(SecretoRastreador.secreto_hash).where(
            SecretoRastreador.rastreador_serial == serial
        )

        return self.db.scalar(consulta)
