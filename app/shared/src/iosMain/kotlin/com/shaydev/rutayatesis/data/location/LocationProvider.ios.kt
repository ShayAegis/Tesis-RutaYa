package com.shaydev.rutayatesis.data.location

import com.shaydev.rutayatesis.domain.model.Point
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.useContents
import platform.CoreLocation.CLLocationManager
import platform.CoreLocation.kCLAuthorizationStatusAuthorizedAlways
import platform.CoreLocation.kCLAuthorizationStatusAuthorizedWhenInUse

@OptIn(ExperimentalForeignApi::class)
actual suspend fun getCurrentLocation(): Point? {
    val manager = CLLocationManager()
    val isAuthorized = when (manager.authorizationStatus) {
        kCLAuthorizationStatusAuthorizedWhenInUse, kCLAuthorizationStatusAuthorizedAlways -> true
        else -> false
    }
    if (!isAuthorized) return null

    val location = manager.location ?: return null
    return location.coordinate.useContents { Point(lat = latitude, lon = longitude) }
}
