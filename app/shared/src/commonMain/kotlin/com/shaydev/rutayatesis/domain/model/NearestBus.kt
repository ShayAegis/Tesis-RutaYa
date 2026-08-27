package com.shaydev.rutayatesis.domain.model

data class NearestBus(
    val busNumber: Int,
    val operatorId: Int,
    val routeCode: String,
    val etaMinutes: Double,
)
