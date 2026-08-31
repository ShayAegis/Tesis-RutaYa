#include "ProvisionDevice.h"
#include "config.h"

bool ProvisionDeviceUsecase::execute(const char* serial, const char* imei){
    String existingSecret = _nvs.getString(nvsSecretKey);
    if(existingSecret.length() > 0) return true;

    String secreto = _repository.provision(serial, imei);
    if(secreto.length() == 0) return false;

    _nvs.putString(nvsSecretKey, secreto.c_str());
    return true;
}
