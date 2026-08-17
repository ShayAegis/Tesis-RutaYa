---
name: firmware-rastreador
description: Contexto sobre el firmware del rastreador (tracker) que envía los datos por MQTT. Úsalo cuando se hable del firmware del rastreador, el dispositivo GPS/tracker, el código que publica por MQTT desde el hardware, o el proyecto de PlatformIO del tracker.
---

Cuando se hable del firmware del rastreador, revisa el proyecto de PlatformIO para entender cómo se generan y envían los datos por MQTT:

/home/shaydev/Documents/PlatformIO/Projects/RutaYa-Tracking

Pasos:
1. Revisa platformio.ini para identificar la placa, librerías usadas (ej. cliente MQTT, GPS) y configuración del entorno
2. Explora src/ para encontrar la lógica de lectura del GPS y publicación MQTT (tópicos, formato del payload, frecuencia de envío)
3. Verifica cómo se estructura el JSON o payload que se publica, para que coincida con lo que espera el servicio mqtt-mongodb (Tesis-mqtt-mongodb)
4. Si hay discrepancias entre el formato que envía el firmware y lo que el servicio backend espera parsear/guardar en MongoDB, señálalas explícitamente
