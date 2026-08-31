#include "PublishTrackingData.h"

constexpr float GEOFENCE_RADIUS_METERS = 500.0f;

PublishTrackingData::PublishTrackingData(Sim7000G& sim, int& seq, TrackerOperatingState& busInfo) : _sim(sim), _seq(seq), _trackerState(busInfo) {}

void PublishTrackingData::_updateDirection(){
    LatLng_t currentPos = _sim.getLatLng();

    if(distanceMeters(currentPos, _trackerState.paradero_inicio) <= GEOFENCE_RADIUS_METERS){
        _esVuelta = false;
    } else if(distanceMeters(currentPos, _trackerState.paradero_final) <= GEOFENCE_RADIUS_METERS){
        _esVuelta = true;
    }
}

TrackingPayloadDto PublishTrackingData::_buildPayload(){
    LatLng_t latlng = _sim.getLatLng();
    float rssi = _sim.getRSSI();
    return {
        .serial  = _serialTracker,
        .placa   = _trackerState.placa,
        .esVuelta  = _esVuelta,
        .lat       = latlng.lat,
        .lon       = latlng.lng,
        .velocidad = _sim.getSpeed(),
        .azimut    = _sim.getAzimuth(),
        .timestamp = (long) _sim.getTimestamp(),
        .seq       = _seq,
        .rssi = rssi
    };
}

String PublishTrackingData::_serializePayload(TrackingPayloadDto data){
    JsonDocument json;
    json["serial"] = data.serial;
    json["placa"] = data.placa;
    json["esVuelta"] = data.esVuelta;
    json["lat"] = data.lat;
    json["lon"] = data.lon;
    json["velocidad"] = data.velocidad;
    json["azimut"] = data.azimut;
    json["timestamp"] = data.timestamp;
    json["seq"] = data.seq;
    json["rssi"] = data.rssi;
    String payload;
    serializeJson(json,payload);
    return payload;
}

bool PublishTrackingData::execute(const char* topic,int qos){
    if(!_sim.isGpsFixed()) return false;
    _updateDirection();
    TrackingPayloadDto payload = _buildPayload();
    String json = _serializePayload(payload);
    bool pubResultOk = _sim.pubMqtt(topic,json.c_str(),qos);
    if(pubResultOk) _seq++;
    return pubResultOk;
}