package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class RutaFavoritaDTO(
    val metadata: RouteMetadataDTO,
    val recorrido: String,
    val bus_cercano: BusCercanoDTO? = null,
)
