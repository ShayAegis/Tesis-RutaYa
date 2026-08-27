package com.shaydev.rutayatesis.data.remote.dto

import com.shaydev.rutayatesis.domain.model.BusTrackingData
import com.shaydev.rutayatesis.domain.model.Point
import kotlinx.serialization.Serializable

@Serializable
data class BusRastreoDTO(
    val lat: Double,
    val lon: Double,
    val velocidad: Float,
    val azimut: Float? = null
){
    fun toDomain(): BusTrackingData{
        return BusTrackingData(
            location = Point(
                lat=this.lat,
                lon=this.lon,
            ),
            speed = this.velocidad,
            azimuth = this.azimut
        )
    }
}
