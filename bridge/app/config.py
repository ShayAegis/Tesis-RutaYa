import os
import uuid
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent.parent / ".env")


def _env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = _env_int("MQTT_PORT", 1883)
MQTT_BASETOPIC = os.getenv("MQTT_BASETOPIC") or None
MQTT_TOPIC = f"{MQTT_BASETOPIC}/#"
MQTT_USERNAME = os.getenv("MQTT_BRIDGE_USERNAME") or None
MQTT_PASSWORD = os.getenv("MQTT_BRIDGE_PASSWORD") or None
MQTT_CLIENT_ID = os.getenv("MQTT_BRIDGE_CLIENT_ID", f"mqtt-mongodb-bridge-{uuid.uuid4().hex[:8]}")
MQTT_KEEPALIVE = _env_int("MQTT_KEEPALIVE", 60)
MQTT_QOS = _env_int("MQTT_QOS", 1)

MONGODB_USER = quote_plus(os.getenv("MONGODB_USER", ""))
MONGODB_PASSWORD = quote_plus(os.getenv("MONGODB_PASSWORD", ""))
MONGO_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{os.getenv("MONGODB_HOST")}:{os.getenv("MONGODB_PORT")}/{os.getenv("MONGODB_NAME")}?authSource=admin"
MONGO_DB = os.getenv("MONGODB_NAME", "tesis")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "bus_positions_history")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = _env_int("REDIS_PORT", 6379)
REDIS_DB = _env_int("REDIS_DB", 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None
