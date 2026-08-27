package com.shaydev.rutayatesis.data.repository

import com.shaydev.rutayatesis.BuildKonfig
import com.shaydev.rutayatesis.data.remote.dto.BusRastreoDTO
import com.shaydev.rutayatesis.domain.model.BusTrackingData
import com.shaydev.rutayatesis.domain.repository.BusRepository
import com.shaydev.rutayatesis.network.NetworkUtils
import io.ktor.client.plugins.sse.sse
import io.ktor.client.request.parameter
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.json.Json

private const val TAG = "ApiBackendBusRepository"

class ApiBackendBusRepository(
    val network: NetworkUtils
) : BusRepository {

    private val json = Json { ignoreUnknownKeys = true }

    override suspend fun getLocationStream(
        busNumber: Int,
        operatorId: Int,
        routeCode: String
    ): Flow<BusTrackingData> {

        val url =
            "${BuildKonfig.API_BASE_URL}/buses/$busNumber/ubicacion/stream"

        return flow {

            network.httpClient.sse(url, request={
                url {
                    parameter("empresaId", operatorId)
                    parameter("rutaId", routeCode)
                }
            }) {
                incoming.collect { stream ->
                    val trackingData = json.decodeFromString<BusRastreoDTO>(stream.data ?: "")
                    emit(trackingData.toDomain())
                }
            }
        }
    }
}

