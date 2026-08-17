import json
import logging
from typing import Any

import paho.mqtt.client as mqtt
from pymongo.collection import Collection

from app import config, redis_store
from app.models.tracker_payload import TrackerPayload
from app.models.tracking_information import TrackingInformation
from app.message import InvalidMessage, parse_payload, parse_topic
from app.storage import get_collection

logger = logging.getLogger(__name__)


def persist(document: dict[str, Any], tracking_information: TrackingInformation, collection: Collection, topic: str) -> None:
    collection.insert_one(document)
    redis_store.save_current_state(redis_store.get_client(), tracking_information, topic)



def _decode_payload(msg: mqtt.MQTTMessage) -> dict[str, Any]:
    return json.loads(msg.payload.decode("utf-8"))


def _parse(msg: mqtt.MQTTMessage, raw: dict[str, Any]) -> TrackerPayload:
    topic = parse_topic(msg.topic)
    return parse_payload(raw, topic)


class MqttMongoBridge:
    def __init__(self) -> None:
        self.collection = get_collection()
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=config.MQTT_CLIENT_ID,
        )
        if config.MQTT_USERNAME:
            self.client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def _on_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,
        _flags: dict,
        reason_code: int,
        _properties: Any = None,
    ) -> None:
        if reason_code != 0:
            logger.error("fallo la conexion a MQTT: %s", reason_code)
            return
        logger.info("conectado a MQTT %s:%s", config.MQTT_HOST, config.MQTT_PORT)
        client.subscribe(config.MQTT_TOPIC, qos=config.MQTT_QOS)
        logger.info("suscrito a topico '%s'", config.MQTT_TOPIC)

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: dict,
        reason_code: int,
        _properties: Any = None,
    ) -> None:
        logger.warning("desconectado de MQTT (reason_code=%s)", reason_code)

    def _on_message(self, _client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            raw = _decode_payload(msg)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning("payload invalido en '%s': %s", msg.topic, exc)
            return

        try:
            payload = _parse(msg, raw)
        except InvalidMessage as exc:
            logger.warning("mensaje rechazado en '%s': %s", msg.topic, exc)
            return

        tracking_information = payload.to_tracker_information(msg.topic)
        document = tracking_information.dump_json()
        persist(document, tracking_information, self.collection, msg.topic)
        logger.info(
            "Mensaje recibido y guardado",
            extra={
                "empresa_id": payload.empresa_id,
                "ruta_codigo": payload.ruta_codigo,
                "numero_bus": payload.numero_bus,
                "serial": payload.serial,
                "lon": payload.lon,
                "lat": payload.lat,
            },
        )

    def run(self) -> None:
        self.client.connect(config.MQTT_HOST, config.MQTT_PORT, config.MQTT_KEEPALIVE)
        self.client.loop_forever()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bridge = MqttMongoBridge()
    bridge.run()


if __name__ == "__main__":
    main()
