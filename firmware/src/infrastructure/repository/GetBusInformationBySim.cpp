#include "GetBusInformationBySim.h"
#include "config.h"
#include <ArduinoJson.h>

TrackerOperatingState BusInformationRepositoryBySim::getTrackerState(){

    String secret = _nvs.getString(nvsSecretKey);
    if(secret.length() == 0){
        Serial.println("[BusInfoRepo] Error: no hay secreto de aprovisionamiento en NVS");
        return TrackerOperatingState{};
    }

    Serial.println("[HTTPS] Info: Obteniendo información del bus desde el backend");
    String endpointWithQuery = String(_endpoint) + "?serial_id=" + serialTracker;
    HTTPRequest request(_baseUrl,endpointWithQuery.c_str(),GET);
    request.addHeader("Rastreador-Secreto",secret.c_str());

    HTTPResponse httpResponse = _sim.httpsBegin(request);

    if(httpResponse.statusCode == 401){
        Serial.println("[BusInfoRepo] Error: secreto rechazado por el servidor, borrando de NVS y reiniciando");
        _nvs.remove(nvsSecretKey);
        ESP.restart();
    }

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
        json["placa"].as<String>(),
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
