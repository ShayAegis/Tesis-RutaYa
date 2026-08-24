import json

from fastapi import FastAPI

from autenticacion import decodificar_token, enrutador as login
from infrastructure.configuracion import configuracion

from application.enrutador_buses import enrutador as enrutador_buses
from application.enrutador_rastreadores import enrutador as enrutador_rastreadores
from application.enrutador_rutas import enrutador as enrutador_rutas
from application.enrutador_usuarios import enrutador as enrutador_usuarios
from application.enrutador_lugares import enrutador as enrutador_lugares
import firebase_admin
from firebase_admin import credentials

produccion = configuracion.production
aplicacion = FastAPI(
    docs_url=None if produccion else "/docs",
    redoc_url=None if produccion else "/redoc",
    openapi_url=None if produccion else "/openapi.json"
)

if produccion:
    from application.middleware.firebase_app_check import comprobar_token_firebase


if configuracion.firebase_credentials_json:
    cred = credentials.Certificate(json.loads(configuracion.firebase_credentials_json))
elif configuracion.firebase_credentials_path:
    cred = credentials.Certificate(configuracion.firebase_credentials_path)
else:
    raise RuntimeError(
        "Debe configurarse FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH"
    )
firebase_admin.initialize_app(cred)

aplicacion.include_router(login)
aplicacion.include_router(enrutador_buses)
aplicacion.include_router(enrutador_rastreadores)
aplicacion.include_router(enrutador_rutas)
aplicacion.include_router(enrutador_usuarios)
aplicacion.include_router(enrutador_lugares)

