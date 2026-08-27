package com.shaydev.rutayatesis.presentation.location

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import kotlinx.cinterop.ExperimentalForeignApi
import platform.CoreLocation.CLLocationManager

@OptIn(ExperimentalForeignApi::class)
@Composable
actual fun rememberLocationPermissionRequester(): () -> Unit {
    val locationManager = remember { CLLocationManager() }
    return remember {
        { locationManager.requestWhenInUseAuthorization() }
    }
}
