#pragma once
#include <Arduino.h>

class IProvisionRepository{
    public:
        virtual String provision(const char* serial, const char* imei) = 0;
        virtual ~IProvisionRepository() = default;
};
