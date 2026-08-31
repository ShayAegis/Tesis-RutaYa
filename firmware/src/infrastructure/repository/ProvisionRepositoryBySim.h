#pragma once
#include "domain/ProvisionRepository.h"
#include "infrastructure/Sim7000.h"

class ProvisionRepositoryBySim : public IProvisionRepository {
    private:
        Sim7000G& _sim;
        const char* _baseUrl;
        const char* _endpoint;
    public:
        String provision(const char* serial, const char* imei) override;
        ProvisionRepositoryBySim(Sim7000G& sim, const char* url, const char* endpoint) : _sim(sim), _baseUrl(url), _endpoint(endpoint) {}
};
