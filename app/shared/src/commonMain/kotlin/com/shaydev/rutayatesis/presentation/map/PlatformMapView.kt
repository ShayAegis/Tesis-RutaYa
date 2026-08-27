package com.shaydev.rutayatesis.presentation.map

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.shaydev.rutayatesis.domain.model.Point

@Composable
expect fun PlatformMapView(
    center: Point,
    zoom: Double,
    modifier: Modifier,
    originMarker: Point? = null,
    destinationMarker: Point? = null,
    busMarker: Point? = null,
    busBearing: Float? = null,
    routeLine: List<Point> = emptyList(),
    walkingLines: List<List<Point>> = emptyList(),
)
