#pragma once
#include <Arduino.h>

struct TrackingPayloadDto{
    String serial;
    bool esVuelta;
    float lat;
    float lon;
    float velocidad;
    float azimut;
    long timestamp;
    int seq;
    float rssi;
};

struct LatLng_t{
    float lat;
    float lng;
};

struct GpsData_t{
    bool fixStatus;
    String dateTime;
    LatLng_t latLng;
    float speed;
    float azimuth;
};

struct TrackerOperatingState{
    int numeroBus;
    int empresaId;
    String ruta_id;
    LatLng_t paradero_inicio;
    LatLng_t paradero_final;
};