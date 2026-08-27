package com.shaydev.rutayatesis.data.remote.dto

import kotlinx.serialization.Serializable

@Serializable
data class PlaceDTO(
    val id: String,
    val nombre_lugar: String,
    val ubicacion: LocationDTO,
    val coincidencia_hasta_indice: Int
)

@Serializable
data class LocationDTO(
    val lat: Float,
    val lon: Float
)