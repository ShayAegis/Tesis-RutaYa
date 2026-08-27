package com.shaydev.rutayatesis.domain.repository

import com.shaydev.rutayatesis.domain.model.BusTrackingData
import kotlinx.coroutines.flow.Flow

interface BusRepository{
    suspend fun getLocationStream(busNumber: Int, operatorId: Int,routeCode: String): Flow<BusTrackingData>
}