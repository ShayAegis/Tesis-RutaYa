#include "domain/models/models.h"
#include "application/usecases/InitializeSystem.h"
#include "application/usecases/PublishTrackingData.h"
#include "application/usecases/GetBusInformation.h"
#include "infrastructure/repository/GetBusInformationBySim.h"
#include "infrastructure/repository/ProvisionRepositoryBySim.h"
#include "infrastructure/NvsStorage.h"
#include "application/usecases/ProvisionDevice.h"
#include "config.h"

int seq = 0;
char mqttTopic[64];

Sim7000G Sim(simRx,simTx,simPwrkey);
NvsStorage nvsStorage(nvsNamespace);
ProvisionRepositoryBySim provisionRepositorySim(Sim,busApiBaseUrl,provisionEndpoint);
ProvisionDeviceUsecase provisionDevice(provisionRepositorySim,nvsStorage);
BusInformationRepositoryBySim busInfoRepositorySim(Sim,nvsStorage,busApiBaseUrl,busApiEndpoint);
GetBusInformationUsecase getTrackerState(busInfoRepositorySim);
InitializeSystem initSystem(Sim, nvsStorage, provisionDevice, getTrackerState);
PublishTrackingData publishTracking(Sim, seq, initSystem.getTrackerState());


void setup(){
    Serial.begin(115200);
    delay(500);
    initSystem.execute();
    Serial.println("Numero de SIM:");
    Serial.println(Sim.getSimNumber());

    TrackerOperatingState& trackerState = initSystem.getTrackerState();

    snprintf(mqttTopic,sizeof(mqttTopic), "%s%d/%s/%d",
            mqttTopicBase,
            trackerState.empresaId,
            trackerState.ruta_id.c_str(),
            trackerState.numeroBus);

}

void loop(){
    Sim.updateGps();
    publishTracking.execute(mqttTopic,mqttQos);
    delay(Sim.isGpsFixed() ? 5000 : 1000);
}