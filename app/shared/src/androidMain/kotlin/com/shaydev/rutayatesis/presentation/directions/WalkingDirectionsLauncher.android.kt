package com.shaydev.rutayatesis.presentation.directions

import android.content.Intent
import android.net.Uri
import com.shaydev.rutayatesis.AndroidContextHolder
import com.shaydev.rutayatesis.domain.model.Point

actual object WalkingDirectionsLauncher {
    actual fun launch(destination: Point) {
        val uri = Uri.parse(
            "https://www.google.com/maps/dir/?api=1" +
                "&destination=${destination.lat},${destination.lon}" +
                "&travelmode=walking"
        )
        val intent = Intent(Intent.ACTION_VIEW, uri).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        AndroidContextHolder.appContext.startActivity(intent)
    }
}
