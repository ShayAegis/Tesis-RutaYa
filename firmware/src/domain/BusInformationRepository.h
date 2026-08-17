#pragma once

#include "models/models.h"

class IBusInformationRepository{
    public:
        virtual TrackerOperatingState getTrackerState() = 0;
        virtual ~IBusInformationRepository() = default;
};