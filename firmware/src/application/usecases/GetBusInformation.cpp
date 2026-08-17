#include "GetBusInformation.h"

TrackerOperatingState GetBusInformationUsecase::execute(){
    return _repository.getTrackerState();
}
