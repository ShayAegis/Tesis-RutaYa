package com.shaydev.rutayatesis.domain.usecase

import com.shaydev.rutayatesis.domain.model.BusTrackingData
import com.shaydev.rutayatesis.domain.model.NearestBus
import com.shaydev.rutayatesis.domain.repository.BusRepository
import kotlinx.coroutines.flow.Flow

class ObserveBusLocationUseCase(
    private val busRepository: BusRepository,
) {
    suspend operator fun invoke(bus: NearestBus): Flow<BusTrackingData> =
        busRepository.getLocationStream(bus.busNumber, bus.operatorId, bus.routeCode)
}
