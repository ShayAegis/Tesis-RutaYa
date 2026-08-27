package com.shaydev.rutayatesis.presentation.directions

import com.shaydev.rutayatesis.domain.model.Point

expect object WalkingDirectionsLauncher {
    fun launch(destination: Point)
}
