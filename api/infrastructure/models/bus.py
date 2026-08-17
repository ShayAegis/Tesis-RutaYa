from typing import List
from datetime import timezone

from annotated_types import Timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, relationship, Mapped
from infrastructure.models.base import Base

class Bus(Base):
    __tablename__ = "busadmin_bus"
    placa: Mapped[str] = mapped_column(String(6),primary_key=True)
    numero_bus: Mapped[int] = mapped_column(Integer)
    empresa_id: Mapped[int] = mapped_column(Integer,ForeignKey('loginuser_empresa.id'))
    empresa: Mapped["Empresa"] = relationship()
    modelo_anio: Mapped[int] = mapped_column(Integer)
    modelo: Mapped[str] = mapped_column(String(50))

class Empresa(Base):
    __tablename__ = "loginuser_empresa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))

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
    asignaciones: Mapped[List["AsignacionRastreador"]] = relationship(back_populates="rastreador")

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