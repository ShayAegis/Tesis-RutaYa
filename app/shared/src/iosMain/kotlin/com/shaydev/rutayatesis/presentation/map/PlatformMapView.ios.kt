package com.shaydev.rutayatesis.presentation.map

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Canvas
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.drawscope.CanvasDrawScope
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.viewinterop.UIKitView
import com.shaydev.rutayatesis.domain.model.Point
import kotlinx.cinterop.ExperimentalForeignApi
import kotlinx.cinterop.IntVar
import kotlinx.cinterop.memScoped
import kotlinx.cinterop.allocArray
import kotlinx.cinterop.get
import kotlinx.cinterop.set
import kotlinx.cinterop.useContents
import org.jetbrains.compose.resources.painterResource
import platform.CoreGraphics.CGAffineTransformMakeRotation
import platform.CoreGraphics.CGBitmapContextCreate
import platform.CoreGraphics.CGBitmapContextCreateImage
import platform.CoreGraphics.CGColorSpaceCreateDeviceRGB
import platform.CoreGraphics.CGColorSpaceRelease
import platform.CoreGraphics.CGContextRelease
import platform.CoreGraphics.CGImageAlphaInfo
import platform.CoreGraphics.CGImageRelease
import platform.CoreGraphics.CGPointMake
import platform.CoreGraphics.CGRectMake
import platform.CoreGraphics.CGSizeMake
import platform.CoreLocation.CLLocationCoordinate2DMake
import platform.CoreLocation.CLLocationCoordinate2D
import platform.MapKit.MKAnnotationProtocol
import platform.MapKit.MKAnnotationView
import platform.MapKit.MKCoordinateRegionMake
import platform.MapKit.MKCoordinateSpanMake
import platform.MapKit.MKMapTypeStandard
import platform.MapKit.MKMapView
import platform.MapKit.MKMapViewDelegateProtocol
import platform.MapKit.MKOverlayProtocol
import platform.MapKit.MKOverlayRenderer
import platform.MapKit.MKPointAnnotation
import platform.MapKit.MKPolyline
import platform.MapKit.MKPolylineRenderer
import platform.MapKit.addOverlay
import platform.MapKit.overlays
import platform.MapKit.removeOverlays
import platform.Foundation.NSNumber
import platform.UIKit.UIBezierPath
import platform.UIKit.UIColor
import platform.UIKit.UIGraphicsImageRenderer
import platform.UIKit.UIImage
import platform.UIKit.systemBlueColor
import platform.UIKit.systemRedColor
import platform.darwin.NSObject
import rutaya_tesis.shared.generated.resources.Res
import rutaya_tesis.shared.generated.resources.ic_bus_tracking
import kotlin.math.PI

private class OriginAnnotation : MKPointAnnotation()
private class DestinationAnnotation : MKPointAnnotation()
private class BusAnnotation : MKPointAnnotation() {
    var azimuth: Double = 0.0
}

private const val BUS_MARKER_HEIGHT_PT = 40.0
private const val BUS_MARKER_VIEWPORT_WIDTH = 253.45
private const val BUS_MARKER_VIEWPORT_HEIGHT = 575.14

// Rasterizes a Compose Painter (works for vector composeResources too) into a UIImage,
// since MapKit annotation views need a plain UIImage rather than a Compose Painter.
@OptIn(ExperimentalForeignApi::class)
private fun rasterizeToUIImage(painter: Painter, width: Int, height: Int): UIImage? {
    if (width <= 0 || height <= 0) return null
    val imageBitmap = ImageBitmap(width, height)
    val canvas = Canvas(imageBitmap)
    val composeCanvas = CanvasDrawScope()
    composeCanvas.draw(
        density = Density(1f),
        layoutDirection = LayoutDirection.Ltr,
        canvas = canvas,
        size = Size(width.toFloat(), height.toFloat()),
    ) {
        with(painter) {
            draw(size = Size(width.toFloat(), height.toFloat()))
        }
    }
    val pixels = IntArray(width * height)
    imageBitmap.readPixels(pixels)
    return memScoped {
        val buffer = allocArray<IntVar>(pixels.size)
        pixels.forEachIndexed { index, value -> buffer[index] = value }
        val colorSpace = CGColorSpaceCreateDeviceRGB()
        val context = CGBitmapContextCreate(
            data = buffer,
            width = width.toULong(),
            height = height.toULong(),
            bitsPerComponent = 8u,
            bytesPerRow = (width * 4).toULong(),
            space = colorSpace,
            bitmapInfo = CGImageAlphaInfo.kCGImageAlphaPremultipliedFirst.value,
        )
        val cgImage = CGBitmapContextCreateImage(context)
        val image = cgImage?.let { UIImage(cGImage = it) }
        cgImage?.let { CGImageRelease(it) }
        context?.let { CGContextRelease(it) }
        colorSpace?.let { CGColorSpaceRelease(it) }
        image
    }
}

// Mirrors ic_origin_marker.xml (1024x1024 viewport, fill #8B5CF6): a pin with a circular hole.
@OptIn(ExperimentalForeignApi::class)
private fun makeOriginMarkerImage(): UIImage {
    val size = CGSizeMake(36.0, 36.0)
    val scale = size.useContents { width } / 1024.0
    val renderer = UIGraphicsImageRenderer(size = size)
    return renderer.imageWithActions { _ ->
        fun pt(x: Double, y: Double) = CGPointMake(x * scale, y * scale)

        UIColor(red = 0.545, green = 0.361, blue = 0.965, alpha = 1.0).setFill()

        val pinPath = UIBezierPath()
        pinPath.moveToPoint(pt(512.0, 85.3))
        pinPath.addCurveToPoint(pt(213.3, 384.0), controlPoint1 = pt(347.1, 85.3), controlPoint2 = pt(213.3, 219.0))
        pinPath.addCurveToPoint(pt(512.0, 938.7), controlPoint1 = pt(213.3, 548.9), controlPoint2 = pt(512.0, 938.7))
        pinPath.addCurveToPoint(pt(810.7, 384.0), controlPoint1 = pt(512.0, 938.7), controlPoint2 = pt(810.7, 549.0))
        pinPath.addCurveToPoint(pt(512.0, 85.3), controlPoint1 = pt(810.7, 219.1), controlPoint2 = pt(677.0, 85.3))
        pinPath.closePath()

        val holeRadius = 149.3
        pinPath.appendPath(
            UIBezierPath.bezierPathWithOvalInRect(
                CGRectMake(
                    (512.0 - holeRadius) * scale,
                    (384.0 - holeRadius) * scale,
                    holeRadius * 2 * scale,
                    holeRadius * 2 * scale,
                ),
            ),
        )
        pinPath.usesEvenOddFillRule = true
        pinPath.fill()
    }
}

// Mirrors ic_destination_marker.xml (16x16 viewport, fill #00C7FC): a checkered flag on a pole.
@OptIn(ExperimentalForeignApi::class)
private fun makeDestinationMarkerImage(): UIImage {
    val size = CGSizeMake(24.0, 24.0)
    val scale = size.useContents { width } / 16.0
    val renderer = UIGraphicsImageRenderer(size = size)
    return renderer.imageWithActions { _ ->
        fun pt(x: Double, y: Double) = CGPointMake(x * scale, y * scale)

        UIColor(red = 0.0, green = 0.780, blue = 0.988, alpha = 1.0).setFill()

        val polePath = UIBezierPath()
        polePath.moveToPoint(pt(1.0, 1.0))
        polePath.addLineToPoint(pt(1.0, 16.0))
        polePath.addLineToPoint(pt(3.0, 16.0))
        polePath.addLineToPoint(pt(3.0, 12.0))
        polePath.addLineToPoint(pt(16.0, 12.0))
        polePath.addLineToPoint(pt(16.0, 1.0))
        polePath.closePath()

        val flagPath = UIBezierPath()
        flagPath.moveToPoint(pt(15.0, 8.0))
        flagPath.addLineToPoint(pt(12.0, 8.0))
        flagPath.addLineToPoint(pt(12.0, 11.0))
        flagPath.addLineToPoint(pt(9.0, 11.0))
        flagPath.addLineToPoint(pt(9.0, 8.0))
        flagPath.addLineToPoint(pt(6.0, 8.0))
        flagPath.addLineToPoint(pt(6.0, 11.0))
        flagPath.addLineToPoint(pt(3.0, 11.0))
        flagPath.addLineToPoint(pt(3.0, 8.0))
        flagPath.addLineToPoint(pt(6.0, 8.0))
        flagPath.addLineToPoint(pt(6.0, 5.0))
        flagPath.addLineToPoint(pt(3.0, 5.0))
        flagPath.addLineToPoint(pt(3.0, 2.0))
        flagPath.addLineToPoint(pt(6.0, 2.0))
        flagPath.addLineToPoint(pt(6.0, 5.0))
        flagPath.addLineToPoint(pt(9.0, 5.0))
        flagPath.addLineToPoint(pt(9.0, 2.0))
        flagPath.addLineToPoint(pt(12.0, 2.0))
        flagPath.addLineToPoint(pt(12.0, 5.0))
        flagPath.addLineToPoint(pt(15.0, 5.0))
        flagPath.closePath()

        polePath.appendPath(flagPath)
        polePath.usesEvenOddFillRule = true
        polePath.fill()
    }
}

@OptIn(ExperimentalForeignApi::class)
private class RouteLineMapDelegate : NSObject(), MKMapViewDelegateProtocol {
    var dashedOverlays: Set<MKPolyline> = emptySet()
    var busMarkerImage: UIImage? = null
    private val originMarkerImage by lazy { makeOriginMarkerImage() }
    private val destinationMarkerImage by lazy { makeDestinationMarkerImage() }

    override fun mapView(mapView: MKMapView, rendererForOverlay: MKOverlayProtocol): MKOverlayRenderer {
        val polyline = rendererForOverlay as? MKPolyline ?: return MKOverlayRenderer(rendererForOverlay)
        val isWalkingLeg = polyline in dashedOverlays
        return MKPolylineRenderer(polyline).apply {
            strokeColor = if (isWalkingLeg) UIColor.systemBlueColor else UIColor.systemRedColor
            lineWidth = 4.0
            if (isWalkingLeg) {
                lineDashPattern = listOf(NSNumber(int = 8), NSNumber(int = 6))
            }
        }
    }

    override fun mapView(mapView: MKMapView, viewForAnnotation: MKAnnotationProtocol): MKAnnotationView? {
        val (identifier, image) = when (viewForAnnotation) {
            is OriginAnnotation -> "origin-marker" to originMarkerImage
            is DestinationAnnotation -> "destination-marker" to destinationMarkerImage
            is BusAnnotation -> "bus-marker" to (busMarkerImage ?: return null)
            else -> return null
        }
        val annotationView = mapView.dequeueReusableAnnotationViewWithIdentifier(identifier)
            ?.apply { this.annotation = viewForAnnotation }
            ?: MKAnnotationView(annotation = viewForAnnotation, reuseIdentifier = identifier)
        annotationView.image = image
        annotationView.centerOffset = CGPointMake(0.0, -image.size.useContents { height } / 2.0)
        val azimuth = (viewForAnnotation as? BusAnnotation)?.azimuth ?: 0.0
        annotationView.transform = CGAffineTransformMakeRotation(azimuth * PI / 180.0)
        return annotationView
    }
}

private const val MIN_SPAN_DEGREES = 0.01
private const val BOUNDS_PADDING_FACTOR = 1.4

@OptIn(ExperimentalForeignApi::class)
private fun regionForBounds(bounds: LatLngBounds) = MKCoordinateRegionMake(
    CLLocationCoordinate2DMake((bounds.north + bounds.south) / 2.0, (bounds.east + bounds.west) / 2.0),
    MKCoordinateSpanMake(
        ((bounds.north - bounds.south).coerceAtLeast(MIN_SPAN_DEGREES)) * BOUNDS_PADDING_FACTOR,
        ((bounds.east - bounds.west).coerceAtLeast(MIN_SPAN_DEGREES)) * BOUNDS_PADDING_FACTOR,
    ),
)

private fun routeBounds(
    originMarker: Point?,
    destinationMarker: Point?,
    busMarker: Point?,
    routeLine: List<Point>,
    walkingLines: List<List<Point>>,
): LatLngBounds? {
    if (routeLine.isEmpty() && walkingLines.isEmpty()) return null
    val points = buildList {
        originMarker?.let { add(it) }
        destinationMarker?.let { add(it) }
        busMarker?.let { add(it) }
        addAll(routeLine)
        walkingLines.forEach { addAll(it) }
    }
    return boundsOf(points)
}

@OptIn(ExperimentalForeignApi::class)
private fun makePolyline(points: List<Point>): MKPolyline = memScoped {
    val coordinates = allocArray<CLLocationCoordinate2D>(points.size)
    points.forEachIndexed { index, point ->
        coordinates[index].latitude = point.lat
        coordinates[index].longitude = point.lon
    }
    MKPolyline.polylineWithCoordinates(coordinates, points.size.toULong())
}

@OptIn(ExperimentalForeignApi::class)
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
    val defaultRegion = remember(center.lat, center.lon, zoom) {
        val coordinate = CLLocationCoordinate2DMake(center.lat, center.lon)
        val zoomAdjust = 0.0005
        val span = MKCoordinateSpanMake(zoom * zoomAdjust,
            zoom * zoomAdjust)
        MKCoordinateRegionMake(coordinate, span)
    }
    val delegate = remember { RouteLineMapDelegate() }
    val busAnnotation = remember { BusAnnotation() }

    val busMarkerPainter = painterResource(Res.drawable.ic_bus_tracking)
    val busMarkerImage = remember(busMarkerPainter) {
        val height = BUS_MARKER_HEIGHT_PT.toInt()
        val width = (height * (BUS_MARKER_VIEWPORT_WIDTH / BUS_MARKER_VIEWPORT_HEIGHT)).toInt()
        rasterizeToUIImage(busMarkerPainter, width, height)
    }
    delegate.busMarkerImage = busMarkerImage

    UIKitView(
        modifier = modifier,
        factory = {
            MKMapView().apply {
                mapType = MKMapTypeStandard
                setRegion(defaultRegion, animated = false)
                setDelegate(delegate)
            }
        },
        update = { mapView ->
            val bounds = routeBounds(originMarker, destinationMarker, busMarker, routeLine, walkingLines)
            mapView.setRegion(bounds?.let(::regionForBounds) ?: defaultRegion, animated = true)
            mapView.removeAnnotations(mapView.annotations)
            if (originMarker != null) {
                val annotation = OriginAnnotation().apply {
                    setCoordinate(CLLocationCoordinate2DMake(originMarker.lat, originMarker.lon))
                }
                mapView.addAnnotation(annotation)
            }
            if (destinationMarker != null) {
                val annotation = DestinationAnnotation().apply {
                    setCoordinate(CLLocationCoordinate2DMake(destinationMarker.lat, destinationMarker.lon))
                }
                mapView.addAnnotation(annotation)
            }
            if (busMarker != null) {
                busAnnotation.azimuth = busBearing?.toDouble() ?: 0.0
                busAnnotation.setCoordinate(CLLocationCoordinate2DMake(busMarker.lat, busMarker.lon))
                mapView.addAnnotation(busAnnotation)
            }
            mapView.removeOverlays(mapView.overlays)
            val walkingPolylines = walkingLines
                .filter { it.size >= 2 }
                .map { makePolyline(it) }
            delegate.dashedOverlays = walkingPolylines.toSet()
            if (routeLine.size >= 2) {
                mapView.addOverlay(makePolyline(routeLine))
            }
            walkingPolylines.forEach { mapView.addOverlay(it) }
        },
    )
}
