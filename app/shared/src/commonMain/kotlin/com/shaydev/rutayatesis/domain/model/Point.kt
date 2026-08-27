package com.shaydev.rutayatesis.domain.model

data class Point(
    val lat: Double,
    val lon: Double
){
    init {
        require(lat in -90.0..90.0) { "latitude out of range" }
        require(lon in -180.0..180.0) { "longitude out of range" }
    }
}
