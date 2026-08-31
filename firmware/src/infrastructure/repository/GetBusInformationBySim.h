#pragma once
#include "domain/BusInformationRepository.h"
#include "infrastructure/Sim7000.h"
#include "infrastructure/NvsStorage.h"

class BusInformationRepositoryBySim : public IBusInformationRepository {
    private:
        Sim7000G& _sim;
        NvsStorage& _nvs;
        const char* _baseUrl;
        const char* _endpoint;
    public:
        TrackerOperatingState getTrackerState() override;
        BusInformationRepositoryBySim(Sim7000G& sim, NvsStorage& nvs, const char* url, const char* endpoint) : _sim(sim), _nvs(nvs), _baseUrl(url), _endpoint(endpoint) {}
};
