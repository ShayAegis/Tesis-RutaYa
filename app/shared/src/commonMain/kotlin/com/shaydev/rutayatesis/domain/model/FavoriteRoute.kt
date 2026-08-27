package com.shaydev.rutayatesis.domain.model

data class FavoriteRoute(
    val id: Int,
    val operator: String,
    val code: String,
    val originPortalName: String,
    val destinationPortalName: String,
    val polyline: List<Point>,
    val nearestBus: NearestBus?,
)
