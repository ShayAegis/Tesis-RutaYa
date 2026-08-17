#pragma once
#include "domain/BusInformationRepository.h"
#include "infrastructure/Sim7000.h"

class BusInformationRepositoryBySim : public IBusInformationRepository {
    private:
        Sim7000G& _sim;
        const char* _baseUrl;
        const char* _endpoint;
    public:
        TrackerOperatingState getTrackerState() override;
        BusInformationRepositoryBySim(Sim7000G& sim, const char* url, const char* endpoint) : _sim(sim), _baseUrl(url), _endpoint(endpoint) {}
};
