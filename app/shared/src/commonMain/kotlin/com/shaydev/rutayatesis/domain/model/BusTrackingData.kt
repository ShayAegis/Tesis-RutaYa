package com.shaydev.rutayatesis.domain.model

data class BusTrackingData(
    val location: Point,
    val speed: Float,
    val azimuth: Float? = null
)
