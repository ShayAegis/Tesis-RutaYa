from sqlalchemy.util import walk_subclasses
from infrastructure.models.base import Base
from infrastructure.models.bus import Empresa
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column, Mapped

class Rastreador(Base):
    __tablename__ = "rastreadoresadmin_rastreador"
    serial: Mapped[str] = mapped_column(String(50),primary_key=True)
    modelo: Mapped[str] = mapped_column(String(100))
    imei: Mapped[str] = mapped_column(String(15))
    iccid: Mapped[str] = mapped_column(String(22))
    operador_red_id: Mapped[int] = mapped_column(Integer,ForeignKey("rastreadoresadmin_operadorredmovil.id"))
    operador_red: Mapped["OperadorRedMovil"] = relationship()
    numero_sim: Mapped[str] = mapped_column(String(15))
    empresa_id: Mapped[int] = mapped_column(Integer,ForeignKey('loginuser_empresa.id'))
    empresa: Mapped["Empresa"] = relationship()
    asignaciones: Mapped[list["AsignacionRastreador"]] = relationship(back_populates="rastreador")

class OperadorRedMovil(Base):
    __tablename__ = "rastreadoresadmin_operadorredmovil"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(20))

class AsignacionRastreador(Base):
    __tablename__ = "busadmin_asignacionrastreadores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_inicio: Mapped[timezone] = mapped_column(DateTime(timezone=True))
    fecha_fin: Mapped[timezone | None] = mapped_column(DateTime(timezone=True))
    bus_id: Mapped[str] = mapped_column(ForeignKey("busadmin_bus.placa"))
    rastreador_id: Mapped[str] = mapped_column(ForeignKey("rastreadoresadmin_rastreador.serial"))
    rastreador: Mapped["Rastreador"] = relationship(
        back_populates="asignaciones"
    )
class SecretoRastreador(Base):
    __tablename__ = "secretorastreador"
    rastreador_serial: Mapped[str] = mapped_column(String(50),ForeignKey("rastreadoresadmin_rastreador.serial"), primary_key=True)
    secreto_hash: Mapped[str] = mapped_column(String(60),nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
