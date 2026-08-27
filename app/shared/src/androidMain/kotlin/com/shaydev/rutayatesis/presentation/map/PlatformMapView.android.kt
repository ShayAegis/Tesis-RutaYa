package com.shaydev.rutayatesis.presentation.map

import android.content.Context
import android.graphics.Color as AndroidColor
import android.graphics.DashPathEffect
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asAndroidBitmap
import androidx.compose.ui.graphics.drawscope.CanvasDrawScope
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.viewinterop.AndroidView
import com.shaydev.rutayatesis.domain.model.Point
import org.jetbrains.compose.resources.painterResource
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox as OsmBoundingBox
import org.osmdroid.util.GeoPoint as OsmGeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.ic_origin_marker
import rutaya_tesis.shared.generated.resources.ic_destination_marker
import rutaya_tesis.shared.generated.resources.ic_bus_tracking
import androidx.core.graphics.drawable.toDrawable

private const val BUS_MARKER_HEIGHT_DP = 40
private const val BUS_MARKER_VIEWPORT_WIDTH = 253.45f
private const val BUS_MARKER_VIEWPORT_HEIGHT = 575.14f

private const val USER_AGENT = "rutaya-tesis/1.0"
private const val ROUTE_LINE_WIDTH = 8f
private const val WALKING_DASH_ON = 12f
private const val WALKING_DASH_OFF = 10f
private const val ROUTE_BOUNDS_PADDING_PX = 96

private fun routeBounds(
    originMarker: Point?,
    destinationMarker: Point?,
    routeLine: List<Point>,
    walkingLines: List<List<Point>>,
): LatLngBounds? {
    if (routeLine.isEmpty() && walkingLines.isEmpty()) return null
    val points = buildList {
        originMarker?.let { add(it) }
        destinationMarker?.let { add(it) }
        addAll(routeLine)
        walkingLines.forEach { addAll(it) }
    }
    return boundsOf(points)
}

@Composable
actual fun PlatformMapView(
    center: Point,
    zoom: Double,
    modifier: Modifier,
    originMarker: Point?,
    destinationMarker: Point?,
    busMarker: Point?,
    busBearing: Float?,
    routeLine: List<Point>,
    walkingLines: List<List<Point>>,
) {
    val context = LocalContext.current
    val mapView = remember { buildMapView(context) }
    val markerOverlay = remember { Marker(mapView) }
    val destinationMarkerOverlay = remember { Marker(mapView) }
    val busMarkerOverlay = remember { Marker(mapView) }
    val routeLineOverlay = remember {
        Polyline(mapView).apply {
            outlinePaint.strokeWidth = ROUTE_LINE_WIDTH
            outlinePaint.color = AndroidColor.RED
        }
    }
    val walkingLineOverlays = remember { mutableListOf<Polyline>() }

    val originMarkerPainter = painterResource(Res.drawable.ic_origin_marker)
    val destinationMarkerPainter = painterResource(Res.drawable.ic_destination_marker)
    val busMarkerPainter = painterResource(Res.drawable.ic_bus_tracking)

    LaunchedEffect(mapView) {
        Configuration.getInstance().userAgentValue = USER_AGENT
        mapView.controller.setZoom(zoom)
        mapView.controller.setCenter(OsmGeoPoint(center.lat, center.lon))
    }

    LaunchedEffect(originMarker) {
        mapView.overlays.remove(markerOverlay)
        if (originMarker != null) {
            markerOverlay.position = OsmGeoPoint(originMarker.lat, originMarker.lon)
            val density = mapView.context.resources.displayMetrics.density
            val sizePx = (36 * density).toInt()

            val imageBitmap = ImageBitmap(sizePx, sizePx)
            val canvas = Canvas(imageBitmap)
            val composeCanvas = CanvasDrawScope()

            composeCanvas.draw(
                density = Density(density),
                layoutDirection = LayoutDirection.Ltr,
                canvas = canvas,
                size = Size(sizePx.toFloat(), sizePx.toFloat())
            ) {
                with(originMarkerPainter) {
                    draw(size = Size(sizePx.toFloat(), sizePx.toFloat()))
                }
            }
            val bitmap = imageBitmap.asAndroidBitmap()
            markerOverlay.icon = bitmap.toDrawable(mapView.context.resources)
            mapView.overlays.add(markerOverlay)
        }
        mapView.invalidate()
    }
    LaunchedEffect(destinationMarker) {
        mapView.overlays.remove(destinationMarkerOverlay)
        if (destinationMarker != null) {
            destinationMarkerOverlay.position =
                OsmGeoPoint(destinationMarker.lat, destinationMarker.lon)
            val density = mapView.context.resources.displayMetrics.density
            val sizePx = (24 * density).toInt()

            val imageBitmap = ImageBitmap(sizePx, sizePx)
            val canvas = Canvas(imageBitmap)
            val composeCanvas = CanvasDrawScope()

            composeCanvas.draw(
                density = Density(density),
                layoutDirection = LayoutDirection.Ltr,
                canvas = canvas,
                size = Size(sizePx.toFloat(), sizePx.toFloat())
            ) {
                with(destinationMarkerPainter) {
                    draw(size = Size(sizePx.toFloat(), sizePx.toFloat()))
                }
            }
            val bitmap = imageBitmap.asAndroidBitmap()
            destinationMarkerOverlay.icon = bitmap.toDrawable(mapView.context.resources)
            mapView.overlays.add(destinationMarkerOverlay)
        }
        mapView.invalidate()
    }

    LaunchedEffect(busMarker, busBearing) {
        mapView.overlays.remove(busMarkerOverlay)
        if (busMarker != null) {
            busMarkerOverlay.position = OsmGeoPoint(busMarker.lat, busMarker.lon)
            busMarkerOverlay.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
            // osmdroid rotates the icon by -rotation internally, so negate to match a clockwise-from-north azimuth.
            busMarkerOverlay.rotation = -(busBearing ?: 0f)

            val density = mapView.context.resources.displayMetrics.density
            val heightPx = (BUS_MARKER_HEIGHT_DP * density).toInt()
            val widthPx = (heightPx * (BUS_MARKER_VIEWPORT_WIDTH / BUS_MARKER_VIEWPORT_HEIGHT)).toInt()

            val imageBitmap = ImageBitmap(widthPx, heightPx)
            val canvas = Canvas(imageBitmap)
            val composeCanvas = CanvasDrawScope()

            composeCanvas.draw(
                density = Density(density),
                layoutDirection = LayoutDirection.Ltr,
                canvas = canvas,
                size = Size(widthPx.toFloat(), heightPx.toFloat())
            ) {
                with(busMarkerPainter) {
                    draw(size = Size(widthPx.toFloat(), heightPx.toFloat()))
                }
            }
            val bitmap = imageBitmap.asAndroidBitmap()
            busMarkerOverlay.icon = bitmap.toDrawable(mapView.context.resources)
            mapView.overlays.add(busMarkerOverlay)
        }
        mapView.invalidate()
    }

    LaunchedEffect(routeLine) {
        mapView.overlays.remove(routeLineOverlay)
        if (routeLine.size >= 2) {
            routeLineOverlay.setPoints(routeLine.map { OsmGeoPoint(it.lat, it.lon) })
            mapView.overlays.add(routeLineOverlay)
        }
        mapView.invalidate()
    }

    LaunchedEffect(walkingLines) {
        walkingLineOverlays.forEach { mapView.overlays.remove(it) }
        walkingLineOverlays.clear()
        walkingLines.filter { it.size >= 2 }.forEach { leg ->
            val overlay = Polyline(mapView).apply {
                outlinePaint.strokeWidth = ROUTE_LINE_WIDTH
                outlinePaint.color = AndroidColor.BLUE
                outlinePaint.pathEffect =
                    DashPathEffect(floatArrayOf(WALKING_DASH_ON, WALKING_DASH_OFF), 0f)
                setPoints(leg.map { OsmGeoPoint(it.lat, it.lon) })
            }
            walkingLineOverlays.add(overlay)
            mapView.overlays.add(overlay)
        }
        mapView.invalidate()
    }

    LaunchedEffect(originMarker, destinationMarker, routeLine, walkingLines) {
        val bounds = routeBounds(originMarker, destinationMarker, routeLine, walkingLines)
        if (bounds != null && (bounds.north > bounds.south || bounds.east > bounds.west)) {
            mapView.post {
                mapView.zoomToBoundingBox(
                    OsmBoundingBox(bounds.north, bounds.east, bounds.south, bounds.west),
                    true,
                    ROUTE_BOUNDS_PADDING_PX,
                )
            }
        }
    }

    AndroidView(
        factory = { mapView },
        modifier = modifier,
    )
}

private fun buildMapView(context: Context): MapView =
    MapView(context).apply {
        setTileSource(TileSourceFactory.MAPNIK)
        setMultiTouchControls(true)
        isHorizontalMapRepetitionEnabled = false
        isVerticalMapRepetitionEnabled = false
    }
