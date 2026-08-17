#pragma once
#include "domain/models/models.h"
#include <Arduino.h>
#include <math.h>

inline float distanceMeters(LatLng_t a, LatLng_t b){
    constexpr float earthRadiusMeters = 6371000.0f;

    float lat1 = radians(a.lat);
    float lat2 = radians(b.lat);
    float deltaLat = radians(b.lat - a.lat);
    float deltaLng = radians(b.lng - a.lng);

    float h = sin(deltaLat / 2) * sin(deltaLat / 2) +
              cos(lat1) * cos(lat2) * sin(deltaLng / 2) * sin(deltaLng / 2);

    float c = 2 * atan2(sqrt(h), sqrt(1 - h));

    return earthRadiusMeters * c;
}
