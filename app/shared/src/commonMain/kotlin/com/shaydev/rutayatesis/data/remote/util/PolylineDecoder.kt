package com.shaydev.rutayatesis.data.remote.util

import com.shaydev.rutayatesis.domain.model.Point

private const val POLYLINE_PRECISION = 1e5

fun decodePolyline(encoded: String): List<Point> {
    val points = mutableListOf<Point>()
    val cursor = PolylineCursor(encoded)
    var lat = 0
    var lon = 0

    while (cursor.hasNext()) {
        lat += cursor.nextValue()
        lon += cursor.nextValue()
        points += Point(lat = lat / POLYLINE_PRECISION, lon = lon / POLYLINE_PRECISION)
    }

    return points
}

private class PolylineCursor(private val encoded: String) {
    private var index = 0

    fun hasNext(): Boolean = index < encoded.length

    fun nextValue(): Int {
        var shift = 0
        var result = 0
        var byte: Int
        do {
            byte = encoded[index++].code - 63
            result = result or ((byte and 0x1f) shl shift)
            shift += 5
        } while (byte >= 0x20)
        return if ((result and 1) != 0) (result shr 1).inv() else (result shr 1)
    }
}
