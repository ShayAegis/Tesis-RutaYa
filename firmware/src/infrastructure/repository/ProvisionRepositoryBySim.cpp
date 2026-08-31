#include "ProvisionRepositoryBySim.h"
#include <ArduinoJson.h>

String ProvisionRepositoryBySim::provision(const char* serial, const char* imei){

    Serial.println("[HTTPS] Info: Aprovisionando rastreador en el backend");

    JsonDocument requestJson;
    requestJson["serial"] = serial;
    requestJson["imei"] = imei;
    String body;
    serializeJson(requestJson, body);
    Serial.println("[ProvisionRepo] Body a enviar: " + body);

    HTTPRequest request(_baseUrl,_endpoint,POST);
    request.addHeader("Content-Type","application/json");
    request.setBody(body.c_str());

    HTTPResponse httpResponse = _sim.httpsBegin(request);

    if(httpResponse.statusCode == 409){
        Serial.println("[ProvisionRepo] Error: este rastreador ya fue registrado. Contacte al administrador del sistema");
        while(true){ delay(1000); }
    }

    if(httpResponse.statusCode != 200){
        Serial.println("[ProvisionRepo] Error: respuesta del servidor con código " + String(httpResponse.statusCode));
        Serial.println("[ProvisionRepo] Contenido de la respuesta: " + httpResponse.content);
        return "";
    }

    JsonDocument json;
    DeserializationError error = deserializeJson(json, httpResponse.content);
    if(error){
        Serial.println("[ProvisionRepo] Error: fallo al parsear la respuesta del servidor");
        return "";
    }

    return json["secreto"].as<String>();
}
