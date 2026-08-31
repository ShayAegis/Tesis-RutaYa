#pragma once
#include "domain/ProvisionRepository.h"
#include "infrastructure/NvsStorage.h"

class ProvisionDeviceUsecase{

    private:
        IProvisionRepository& _repository;
        NvsStorage& _nvs;
    public:
        bool execute(const char* serial, const char* imei);
        ProvisionDeviceUsecase(IProvisionRepository& repository, NvsStorage& nvs) : _repository(repository), _nvs(nvs) {}
};
