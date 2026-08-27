package com.shaydev.rutayatesis.presentation.map

import com.shaydev.rutayatesis.domain.model.Point

data class LatLngBounds(
    val north: Double,
    val south: Double,
    val east: Double,
    val west: Double,
)

fun boundsOf(points: List<Point>): LatLngBounds? {
    if (points.isEmpty()) return null
    var north = points[0].lat
    var south = points[0].lat
    var east = points[0].lon
    var west = points[0].lon
    for (point in points) {
        if (point.lat > north) north = point.lat
        if (point.lat < south) south = point.lat
        if (point.lon > east) east = point.lon
        if (point.lon < west) west = point.lon
    }
    return LatLngBounds(north = north, south = south, east = east, west = west)
}
