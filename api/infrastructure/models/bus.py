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


