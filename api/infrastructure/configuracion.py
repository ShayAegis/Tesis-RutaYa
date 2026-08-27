from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
class Configuracion(BaseSettings):
    production: bool
    oauth2_secret_key: str
    oauth2_algorithm: str
    oauth2_access_token_expiration_minutes: int
    oauth2_refresh_token_expiration_days: int
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    redis_host: str
    redis_port: int
    redis_password: str
    redis_db: int
    redis_max_connections: int = 200
    mongodb_host: str
    mongodb_port: int
    mongodb_name: str
    mongodb_user: str
    mongodb_password: str
    mqtt_basetopic: str
    mqtt_host: str
    mqtt_port: int
    mqtt_qos: int
    places_api_key: str
    osrm_host:str
    firebase_credentials_path: str | None = None
    firebase_credentials_json: str | None = None
    broker_key: str
    class Config:
        env_file = BASE_DIR.parent / ".env"
        extra = "ignore"


configuracion = Configuracion()
