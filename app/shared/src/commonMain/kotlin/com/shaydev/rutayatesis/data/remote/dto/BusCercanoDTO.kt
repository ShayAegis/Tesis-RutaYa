package com.shaydev.rutayatesis.data.remote.dto

import com.shaydev.rutayatesis.domain.model.NearestBus
import kotlinx.serialization.Serializable

@Serializable
data class BusCercanoDTO(
    val numero_bus: Int,
    val empresa_id: Int,
    val ruta: String,
    val eta_minutos: Double,
)

fun BusCercanoDTO.toDomain() = NearestBus(
    busNumber = numero_bus,
    operatorId = empresa_id,
    routeCode = ruta,
    etaMinutes = eta_minutos,
)
