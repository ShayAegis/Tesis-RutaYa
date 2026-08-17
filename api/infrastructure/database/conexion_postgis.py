from typing import Any, Generator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.configuracion import configuracion

url_base_datos = URL.create(
    drivername="postgresql+psycopg2",
    host=configuracion.db_host,
    port=configuracion.db_port,
    username=configuracion.db_user,
    password=configuracion.db_password,
    database=configuracion.db_name
)

motor_bd = create_engine(url_base_datos)

SesionLocal = sessionmaker(bind=motor_bd,
                       autoflush=False,
                       autocommit=False)


def obtener_sesion_bd() -> Generator[Session,None,None]:
    with SesionLocal() as sesion:
        yield sesion
