from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.models.base import Base
from infrastructure.models.ruta import Ruta, rutas_favoritas


class Usuario(Base):
    __tablename__ = "loginuser_usuario"
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String(128))
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_superuser: Mapped[bool] = mapped_column()
    username: Mapped[str] = mapped_column(String(150))
    first_name: Mapped[str] = mapped_column(String(150))
    last_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(254))
    is_staff: Mapped[bool] = mapped_column()
    is_active: Mapped[bool] = mapped_column()
    date_joined: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    empresa_id: Mapped[int | None] = mapped_column(ForeignKey("loginuser_empresa.id"))
    rutas_favoritas: Mapped[List["Ruta"]] = relationship(secondary=rutas_favoritas)

class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("loginuser_usuario.id"))
    usuario: Mapped["Usuario"] = relationship()
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
