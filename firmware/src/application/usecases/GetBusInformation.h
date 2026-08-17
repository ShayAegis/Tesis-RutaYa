#pragma once
#include "domain/BusInformationRepository.h"
#include "domain/models/models.h"

class GetBusInformationUsecase{

    private:
        IBusInformationRepository& _repository; 
    public:
        TrackerOperatingState execute();
        GetBusInformationUsecase(IBusInformationRepository& repository) : _repository(repository){} 
};