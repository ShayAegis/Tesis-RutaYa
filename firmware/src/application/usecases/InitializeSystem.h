// application/usecases/InitializeSystem.h
#pragma once
#include "infrastructure/Sim7000.h"
#include "infrastructure/NvsStorage.h"
#include "application/usecases/GetBusInformation.h"
#include "application/usecases/ProvisionDevice.h"
#include "config.h"

class InitializeSystem {
    private:
        Sim7000G& _sim;
        NvsStorage& _nvs;
        ProvisionDeviceUsecase& _provisionDevice;
        GetBusInformationUsecase& _getBusInfo;
        TrackerOperatingState _trackerState;

        bool _initModem() {
            if (!_sim.begin()) {
                Serial.println("[SIM] Error: módulo no responde");
                return false;
            }
            Serial.println("[SIM] Módulo inicializado correctamente");
            return true;
        }

        bool _initNetwork() {
            if (!_sim.connectNetwork(apn)) {
                Serial.println("[NET] Error: no se pudo conectar a la red");
                return false;
            }
            Serial.println("[NET] Red conectada");
            return true;
        }

        bool _initProvisioning() {
            String imei = _sim.getImei();
            if (!_provisionDevice.execute(serialTracker, imei.c_str())) {
                Serial.println("[PROV] Error: no se pudo aprovisionar el rastreador");
                return false;
            }
            Serial.println("[PROV] Rastreador aprovisionado");
            return true;
        }

        bool _initBusInfo() {
            _trackerState = _getBusInfo.execute();
            if (_trackerState.numeroBus == 0) {
                Serial.println("[BUS] Error: no se pudo obtener información del bus");
                return false;
            }
            Serial.println("[BUS] Información del bus obtenida");
            return true;
        }

        bool _initMqtt() {
            Serial.println("[MQTT] Conectando a broker...");
            String secret = _nvs.getString(nvsSecretKey);
            if (!_sim.mqttConnect("sim7000g", mqttBrokerUrl, mqttPort, serialTracker, secret.c_str())) {
                Serial.println("[MQTT] Error: conexión al broker falló");
                return false;
            }
            Serial.println("[MQTT] Conectado al broker");
            return true;
        }

        void _initTime() {
            _sim.syncNTP("pool.ntp.org");
            Serial.println("[NTP] Tiempo sincronizado");
        }

        void _initGps() {
            Serial.println("[GPS] Inicializando con AGPS...");
            _sim.gpsBegin(true);
        }

    public:
        InitializeSystem(Sim7000G& sim, NvsStorage& nvs, ProvisionDeviceUsecase& provisionDevice, GetBusInformationUsecase& getBusInfo) : _sim(sim), _nvs(nvs), _provisionDevice(provisionDevice), _getBusInfo(getBusInfo) {}

        bool execute() {
            if (!_initModem())   return false;
            if (!_initNetwork()) return false;
            if (!_initProvisioning()) return false;
            if (!_initBusInfo()) return false;
            if (!_initMqtt())    return false;
            _initTime();
            _initGps();
            return true;
        }

        TrackerOperatingState& getTrackerState() {
            return _trackerState;
        }
};