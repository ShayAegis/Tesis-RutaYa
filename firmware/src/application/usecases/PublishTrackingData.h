#pragma once
#include "config.h"
#include "domain/models/models.h"
#include "domain/GeoUtils.h"
#include "infrastructure/Sim7000.h"
#include <ArduinoJson.h>


class PublishTrackingData{
    private:
        Sim7000G& _sim;
        int& _seq;
        String _serialTracker = serialTracker;
        TrackerOperatingState& _trackerState;
        bool _esVuelta = false;
        TrackingPayloadDto _buildPayload();
        String _serializePayload(TrackingPayloadDto data);
        void _updateDirection();
    public:
        PublishTrackingData(Sim7000G& sim, int& seq, TrackerOperatingState& busInfo);
        bool execute(const char* topic,int qos);
};