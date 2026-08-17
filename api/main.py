from fastapi import FastAPI

from autenticacion import enrutador as login

from application.enrutador_buses import enrutador as enrutador_buses
from application.enrutador_rastreadores import enrutador as enrutador_rastreadores
from application.enrutador_rutas import enrutador as enrutador_rutas
from application.enrutador_usuarios import enrutador as enrutador_usuarios
from application.enrutador_lugares import enrutador as enrutador_lugares

aplicacion = FastAPI()

aplicacion.include_router(login)
aplicacion.include_router(enrutador_buses)
aplicacion.include_router(enrutador_rastreadores)
aplicacion.include_router(enrutador_rutas)
aplicacion.include_router(enrutador_usuarios)
aplicacion.include_router(enrutador_lugares)

