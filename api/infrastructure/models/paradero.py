from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from infrastructure.models.base import Base

class Paradero(Base):
    __tablename__ = "paraderosadmin_paradero"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    radio: Mapped[float] = mapped_column(Float())
    ubicacion: Mapped[object] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326)
    )