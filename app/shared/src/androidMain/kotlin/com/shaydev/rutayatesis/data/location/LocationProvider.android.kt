package com.shaydev.rutayatesis.data.location

import android.content.Context
import android.content.pm.PackageManager
import android.location.LocationManager
import androidx.core.content.ContextCompat
import com.shaydev.rutayatesis.AndroidContextHolder
import com.shaydev.rutayatesis.domain.model.Point

actual suspend fun getCurrentLocation(): Point? {
    val context = AndroidContextHolder.appContext
    val hasPermission = ContextCompat.checkSelfPermission(
        context, android.Manifest.permission.ACCESS_FINE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED || ContextCompat.checkSelfPermission(
        context, android.Manifest.permission.ACCESS_COARSE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED
    if (!hasPermission) return null

    val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
    val location = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
        .filter { locationManager.isProviderEnabled(it) }
        .mapNotNull { runCatching { locationManager.getLastKnownLocation(it) }.getOrNull() }
        .maxByOrNull { it.time }
        ?: return null

    return Point(lat = location.latitude, lon = location.longitude)
}
