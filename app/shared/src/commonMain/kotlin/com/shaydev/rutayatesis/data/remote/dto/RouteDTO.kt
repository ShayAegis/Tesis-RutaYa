package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class RouteDTO(
    val metadata: RouteMetadataDTO,
    val viaje: TripDTO,
    val retorno: Boolean
)

@Serializable
data class RouteMetadataDTO(
    val id: Int,
    val empresa: String,
    val codigo: String,
    val paradero_inicio: String,
    val paradero_final: String
)

@Serializable
data class TripDTO(
    val itinerario: List<TripLegDTO>,
    val distancia: Double,
    val eta: Double,
    val punto_abordaje: PointDTO? = null
)

@Serializable
data class TripLegDTO(
    val perfil: String,
    val geometria: String
)

@Serializable
data class PointDTO(
    val lat: Double,
    val lon: Double
)
