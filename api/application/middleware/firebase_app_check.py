from main import aplicacion
from fastapi import Request, status
from fastapi.responses import JSONResponse
from firebase_admin import app_check

RUTAS_EXCLUIDAS = ["/rastreadores/me","/docs"]

@aplicacion.middleware("http")
async def comprobar_token_firebase(solicitud: Request,call_next):
    if solicitud.url.path in RUTAS_EXCLUIDAS:
        return await call_next(solicitud)
    token_app_check = solicitud.headers.get("X-Firebase-AppCheck")
    if token_app_check is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail":"Falta el token de Firebase App Check"}
        )
    try:
        app_check.verify_token(token_app_check)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail":"Token de Firebase App Check inválido"}
        )
    respuesta = await call_next(solicitud)
    return respuesta
