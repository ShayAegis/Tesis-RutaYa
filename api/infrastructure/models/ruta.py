from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, DateTime, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from infrastructure.models.base import Base
from infrastructure.models.bus import Bus,Empresa
from infrastructure.models.paradero import Paradero

class AsignacionRuta(Base):
    __tablename__ = "busadmin_asignacionruta"
    id: Mapped[int] = mapped_column(primary_key=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bus_id: Mapped[str] = mapped_column(ForeignKey("busadmin_bus.placa"))
    ruta_id: Mapped[int] = mapped_column(ForeignKey("rutasadmin_ruta.id"))
    bus: Mapped["Bus"] = relationship()
    ruta: Mapped["Ruta"] = relationship()

class Ruta(Base):
    __tablename__ = "rutasadmin_ruta"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(100))
    distancia_km : Mapped[float] = mapped_column(Float)
    paradero_inicio_id: Mapped[int] = mapped_column(ForeignKey("paraderosadmin_paradero.id"))
    paradero_final_id : Mapped[int] = mapped_column(ForeignKey("paraderosadmin_paradero.id"))
    empresa_id : Mapped[int] = mapped_column(ForeignKey("loginuser_empresa.id"))
    recorrido : Mapped[object] = mapped_column(
        Geometry(geometry_type='MULTILINESTRING', srid=4326)
    )
    paradero_inicio: Mapped["Paradero"] = relationship(foreign_keys=[paradero_inicio_id])
    empresa: Mapped["Empresa"] = relationship()
    paradero_final: Mapped["Paradero"] = relationship(foreign_keys=[paradero_final_id])

rutas_favoritas = Table(
    "usuario_rutafavorita",
    Base.metadata,
    Column("ruta_id", ForeignKey("rutasadmin_ruta.id"), primary_key=True),
    Column("usuario_id", ForeignKey("loginuser_usuario.id"),primary_key=True),
)
