from pydantic import BaseModel

class Rastreador(BaseModel):
    serial: str
    modelo: str
    imei: str
    iccid: str
    operador_red: str
    numero_sim: str
    empresa: str
