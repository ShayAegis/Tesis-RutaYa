#include "GetBusInformationBySim.h"
#include <ArduinoJson.h>

TrackerOperatingState BusInformationRepositoryBySim::getTrackerState(){

    Serial.println("[HTTPS] Info: Obteniendo información del bus desde el backend");
    HTTPRequest request(_baseUrl,_endpoint,GET);
    request.addHeader("Rastreador-Serial","RY-TR-2026-0001");

    HTTPResponse httpResponse = _sim.httpsBegin(request);

    if(httpResponse.statusCode != 200){
        Serial.println("[BusInfoRepo] Error: respuesta del servidor con código " + String(httpResponse.statusCode));
        return TrackerOperatingState{};
    }

    JsonDocument json;
    DeserializationError error = deserializeJson(json, httpResponse.content);
    if(error){
        Serial.println("[BusInfoRepo] Error: fallo al parsear la respuesta del servidor");
        return TrackerOperatingState{};
    }

    return TrackerOperatingState{
        json["numero_bus"].as<int>(),
        json["empresa_id"].as<int>(),
        json["ruta"].as<String>(),
        {
            json["paradero_inicio"]["lat"].as<float>(),
            json["paradero_inicio"]["lon"].as<float>()
        },
        {
            json["paradero_final"]["lat"].as<float>(),
            json["paradero_final"]["lon"].as<float>()
        }
    };
}
