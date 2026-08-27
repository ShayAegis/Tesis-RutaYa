package com.shaydev.rutayatesis.domain.model

data class Route(
    val id: Int,
    val operator: String,
    val code: String,
    val distanceKm: Float,
    val etaSeconds: Double,
    val originPortalName: String,
    val destinationPortalName: String,
    val returnWay: Boolean,
    val busLegPolyline: List<Point>,
    val walkingLegPolylines: List<List<Point>>,
    val boardingPoint: Point?
)
