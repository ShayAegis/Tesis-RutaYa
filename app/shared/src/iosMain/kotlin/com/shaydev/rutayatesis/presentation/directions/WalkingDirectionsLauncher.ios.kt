package com.shaydev.rutayatesis.presentation.directions

import com.shaydev.rutayatesis.domain.model.Point
import platform.Foundation.NSURL
import platform.UIKit.UIApplication

actual object WalkingDirectionsLauncher {
    actual fun launch(destination: Point) {
        val url = NSURL(string = "https://maps.apple.com/?daddr=${destination.lat},${destination.lon}&dirflg=w")
        UIApplication.sharedApplication.openURL(url)
    }
}
